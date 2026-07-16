"""Experimental shared arm runner. Production pipelines intentionally do not import this."""

import json
import os
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from types import SimpleNamespace

from trl import SFTConfig

from reasoning_core.training.checkpointing import (
    ResumableCheckpointCallback,
    latest_complete_checkpoint,
    prepare_checkpoint_dir,
)
from reasoning_core.training.local_metrics import LocalMetricsCallback, LocalMetricsSink
from reasoning_core.training.optimizers import create_optimizer_and_scheduler, trainer_cls_for_optimizer
from reasoning_core.training.paths import RUNS_HOME, home_path


@dataclass(frozen=True)
class ArmSpec:
    experiment_id: str
    arm_id: str
    optimizer: str = "prodigy"
    max_steps: int = 10
    batch_size: int = 1
    gradient_accumulation_steps: int = 1
    max_length: int = 128
    checkpoint_every_minutes: float = 60
    decay: float = 0.01
    adamc_weight_decay: float = 20.0
    adamc_r: float = 0.0
    seed: int = 0
    save_final: bool = False

    @property
    def run_dir(self):
        return home_path(RUNS_HOME / "dev" / self.experiment_id / "arms" / safe_name(self.arm_id))


def format_qa(prompt, answer, eos_token):
    """Canonical production run_sft QA format."""
    return {"prompt": f"Q: {prompt}\nA:", "completion": f" {answer}{eos_token}"}


def train_arm(model, tokenizer, dataset, spec, eval_dataset=None, callbacks=()):
    run_dir = spec.run_dir
    prepare_checkpoint_dir(run_dir)
    status_path = run_dir / "status.json"
    status = _read_json(status_path)
    if status and status.get("state") == "complete":
        return None, status["metrics"]
    sink = LocalMetricsSink(
        run_dir / "metrics.jsonl",
        run_hash=f"{spec.experiment_id}/{spec.arm_id}",
        group_id=spec.experiment_id,
        script_args=SimpleNamespace(**asdict(spec), stage_name=spec.arm_id),
        eff_batch=spec.batch_size * spec.gradient_accumulation_steps,
    )
    optimizer_args = SimpleNamespace(**asdict(spec), train_source_loss=False)
    optimizer, scheduler = create_optimizer_and_scheduler(model, optimizer_args)
    trainer_cls = schedule_free_trainer(trainer_cls_for_optimizer(optimizer_args))
    checkpoint = ResumableCheckpointCallback(
        spec.checkpoint_every_minutes, save_final=spec.save_final,
    )
    trainer = trainer_cls(
        model=model,
        processing_class=tokenizer,
        train_dataset=dataset,
        eval_dataset=eval_dataset,
        optimizers=(optimizer, scheduler),
        callbacks=[LocalMetricsCallback(sink), checkpoint, *callbacks],
        args=SFTConfig(
            output_dir=str(run_dir),
            max_steps=spec.max_steps,
            per_device_train_batch_size=spec.batch_size,
            gradient_accumulation_steps=spec.gradient_accumulation_steps,
            learning_rate=1.0,
            max_grad_norm=0.0,
            max_length=spec.max_length,
            completion_only_loss=True,
            packing=False,
            bf16=False,
            report_to="none",
            logging_steps=1,
            save_strategy="steps",
            save_steps=10**12,
            save_total_limit=1,
            seed=spec.seed,
            disable_tqdm=True,
        ),
    )
    resume = latest_complete_checkpoint(run_dir)
    result = trainer.train(resume_from_checkpoint=resume)
    if checkpoint.interrupted:
        _write_json(status_path, {"state": "interrupted", "spec": asdict(spec)})
        return trainer, None
    metrics = {"train_loss": result.training_loss, "global_step": trainer.state.global_step}
    if eval_dataset is not None:
        metrics.update(trainer.evaluate())
    _write_json(status_path, {"state": "complete", "spec": asdict(spec), "metrics": metrics})
    return trainer, metrics


def record_event(spec, kind, metrics):
    path = spec.run_dir.parent.parent / "events.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {"experiment_id": spec.experiment_id, "arm_id": spec.arm_id, "kind": kind, **metrics}
    encoded = json.dumps(row, sort_keys=True)
    if path.exists() and encoded in path.read_text().splitlines():
        return
    with path.open("a") as f:
        f.write(encoded + "\n")


def schedule_free_trainer(base):
    class DevTrainer(ScheduleFreeTrainerMixin, base):
        pass
    return DevTrainer


class ScheduleFreeTrainerMixin:
    def evaluate(self, *args, **kwargs):
        with optimizer_eval_mode(self.optimizer):
            return super().evaluate(*args, **kwargs)

    def _save_checkpoint(self, *args, **kwargs):
        with optimizer_eval_mode(self.optimizer):
            return super()._save_checkpoint(*args, **kwargs)


@contextmanager
def optimizer_eval_mode(optimizer):
    inner = optimizer
    while hasattr(inner, "optimizer"):
        inner = inner.optimizer
    was_training = any(group.get("train_mode", True) for group in inner.param_groups)
    optimizer.eval()
    try:
        yield
    finally:
        (optimizer.train if was_training else optimizer.eval)()


def safe_name(value):
    return "".join(c if c.isalnum() or c in "._-" else "_" for c in value)


def _write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)


def _read_json(path):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return None
