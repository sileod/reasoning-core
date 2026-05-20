import argparse
import json
import random
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

from datasets import IterableDataset
from transformers import TrainerCallback


__all__ = [
    "add_mix_ablation_args",
    "wrap_aux_dataset_with_ablation",
    "MixAblationCallback",
]


def add_mix_ablation_args(parser):
    parser.add_argument("--mix_ablation", type=_str_to_bool, nargs="?", const=True, default=True)
    parser.add_argument("--ablation_group_map", type=str, default="configs/task_groups_v1.json")
    parser.add_argument("--ablation_unit", choices=("group", "task"), default="task")
    parser.add_argument("--ablation_drop_rates", type=str, default="0,0.25,0.5,1")
    parser.add_argument("--ablation_window_steps", type=int, default=50)
    parser.add_argument("--ablation_target_passes", type=float, default=1.5)
    parser.add_argument("--ablation_min_window_steps", type=int, default=8)
    parser.add_argument("--ablation_max_window_steps", type=int, default=50)
    parser.add_argument("--ablation_control_frac", type=float, default=0.2)
    parser.add_argument("--ablation_log_path", type=str, default="")
    parser.add_argument("--eval_main_override", type=str, default="")
    parser.add_argument("--eval_main_budget", type=int, default=50_000)
    parser.add_argument("--eval_main_skip", type=int, default=1_000_000)
    parser.add_argument("--eval_aux_budget", type=int, default=1_500_000)
    parser.add_argument("--eval_aux_skip", type=int, default=100_000)
    parser.add_argument("--eval_aux_max_scanned", type=int, default=50_000)
    parser.add_argument("--ablation_compute_ratios", type=_str_to_bool, nargs="?", const=True, default=True)
    parser.add_argument("--ablation_wandb_analysis", type=_str_to_bool, nargs="?", const=True, default=True)
    parser.add_argument("--ablation_analysis_min_rows", type=int, default=30)
    parser.add_argument("--ablation_analysis_every_rows", type=int, default=5)
    parser.add_argument("--ablation_analysis_step_df", type=int, default=2)


def wrap_aux_dataset_with_ablation(aux_ds, args, eff_batch):
    task_to_group = _load_group_map(args.ablation_group_map)
    drop_rates = _parse_drop_rates(args.ablation_drop_rates)
    groups = sorted(set(task_to_group.values()))
    if not groups:
        groups = ["unknown"]
    ablation_unit = str(getattr(args, "ablation_unit", "group"))
    if ablation_unit == "task":
        units = sorted(task_to_group)
    else:
        units = groups
    window_steps = _window_steps_for_budget(args, units, drop_rates, eff_batch)

    aux_probability = _aux_probability(getattr(args, "aux_ratio", 0.0))
    window_aux_examples = max(
        1,
        round(window_steps * int(eff_batch) * aux_probability),
    )

    tracker = MixAblationTracker(
        task_to_group=task_to_group,
        groups=groups,
        units=units,
        ablation_unit=ablation_unit,
        drop_rates=drop_rates,
        window_aux_examples=window_aux_examples,
        window_steps=window_steps,
        control_frac=float(args.ablation_control_frac),
        seed=int(getattr(args, "seed", 0)),
        aux_ratio=float(getattr(args, "aux_ratio", 0.0)),
        log_path=args.ablation_log_path or "mix_ablation.jsonl",
        wandb_analysis=(
            bool(getattr(args, "ablation_wandb_analysis", True))
            and bool(getattr(args, "ablation_compute_ratios", True))
        ),
        analysis_min_rows=int(getattr(args, "ablation_analysis_min_rows", 30)),
        analysis_every_rows=int(getattr(args, "ablation_analysis_every_rows", 5)),
        analysis_step_df=int(getattr(args, "ablation_analysis_step_df", 4)),
    )

    def gen():
        rng = random.Random(int(getattr(args, "seed", 0)) + 1729)
        for ex in aux_ds:
            unit = tracker.unit_for_example(ex)
            if tracker.should_drop(unit, rng):
                continue
            yield ex

    return IterableDataset.from_generator(gen), tracker


class MixAblationCallback(TrainerCallback):
    def __init__(self, tracker):
        self.tracker = tracker
        self.previous_loss = None
        self.last_logged_step = None
        self.eval_rows = 0
        self.analysis_warning_printed = False

    def on_log(self, args, state, control, logs=None, **kwargs):
        logs = logs or {}
        loss = _pick_main_loss(logs)
        if loss is None or self.last_logged_step == state.global_step:
            return

        delta = None
        if self.previous_loss is not None:
            delta = loss - self.previous_loss
        self.previous_loss = loss
        self.last_logged_step = state.global_step
        self.tracker.write_eval_row(
            step=int(state.global_step),
            eval_main_loss=loss,
            eval_main_loss_delta=delta,
        )
        self.eval_rows += 1
        self._maybe_log_wandb_analysis(step=int(state.global_step))

    def _maybe_log_wandb_analysis(self, step):
        if not self.tracker.wandb_analysis:
            return
        if self.eval_rows < self.tracker.analysis_min_rows:
            return
        every = max(1, self.tracker.analysis_every_rows)
        if self.eval_rows % every:
            return

        try:
            import wandb

            if wandb.run is None:
                return
            from reasoning_core.training.analyze_mix_ablation import analyze_log_path

            result = analyze_log_path(self.tracker.log_path, step_df=self.tracker.analysis_step_df)
            metrics = {"mix_ablation/analysis_rows": int(self.eval_rows)}
            for row in result.to_dict(orient="records"):
                unit = _clean_metric_fragment(row["unit"])
                metrics[f"mix_ablation/best_drop_rate/{unit}"] = float(row["best_drop_rate"])
                metrics[f"mix_ablation/recommended_keep_ratio/{unit}"] = float(row["recommended_keep_ratio"])
                metrics[f"mix_ablation/stderr/{unit}"] = float(row["stderr"])
                metrics[f"mix_ablation/effect/{unit}"] = float(row["effect"])
            wandb.log(metrics, step=step)
        except Exception as exc:  # Keep training independent from analysis dependencies.
            if not self.analysis_warning_printed:
                print(f"mix_ablation W&B analysis disabled after error: {exc}")
                self.analysis_warning_printed = True


@dataclass
class MixAblationTracker:
    task_to_group: dict
    groups: list
    units: list
    ablation_unit: str
    drop_rates: list
    window_aux_examples: int
    window_steps: int
    control_frac: float
    seed: int
    aux_ratio: float
    log_path: str
    wandb_analysis: bool = True
    analysis_min_rows: int = 30
    analysis_every_rows: int = 5
    analysis_step_df: int = 4
    lock: Lock = field(default_factory=Lock)
    consumed_in_window: int = 0
    target_unit: str | None = None
    drop_rate: float = 0.0
    kept: Counter = field(default_factory=Counter)
    dropped: Counter = field(default_factory=Counter)
    history: deque = field(default_factory=lambda: deque(maxlen=3))

    def __post_init__(self):
        self.rng = random.Random(self.seed + 104729)
        self.schedule = []
        self._refill_schedule()
        self._advance_window()
        path = Path(self.log_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    def unit_for_example(self, ex):
        task = _get_task(ex)
        if task is None:
            return "unknown"
        task = str(task)
        if self.ablation_unit == "task":
            return task if task in self.task_to_group else "unknown"
        return self.task_to_group.get(task, "unknown")

    def should_drop(self, unit, rng):
        with self.lock:
            if self.consumed_in_window >= self.window_aux_examples:
                self._advance_window()
            self.consumed_in_window += 1
            should_drop = (
                self.target_unit is not None
                and unit == self.target_unit
                and rng.random() < self.drop_rate
            )
            if should_drop:
                self.dropped[unit] += 1
            else:
                self.kept[unit] += 1
            return should_drop

    def write_eval_row(self, step, eval_main_loss, eval_main_loss_delta):
        with self.lock:
            target_group = self.group_for_unit(self.target_unit)
            target_task = self.target_unit if self.ablation_unit == "task" else None
            row = {
                "step": step,
                "target_unit": self.target_unit,
                "target_unit_type": self.ablation_unit,
                "target_group": target_group,
                "target_task": target_task,
                "drop_rate": self.drop_rate,
                "eval_main_loss": eval_main_loss,
                "eval_main_loss_delta": eval_main_loss_delta,
                "aux_ratio": self.aux_ratio,
                "window_aux_examples": self.window_aux_examples,
                "window_steps": self.window_steps,
            }
            count_prefix = "task" if self.ablation_unit == "task" else "group"
            for unit, count in sorted(self.kept.items()):
                row[f"kept_{count_prefix}/{unit}"] = count
                if self.ablation_unit == "group":
                    row[f"kept/{unit}"] = count
            for unit, count in sorted(self.dropped.items()):
                row[f"dropped_{count_prefix}/{unit}"] = count
                if self.ablation_unit == "group":
                    row[f"dropped/{unit}"] = count
            for lag, state in enumerate(reversed(list(self.history)[-3:]), start=1):
                row[f"lag{lag}_target_unit"] = state["target_unit"]
                row[f"lag{lag}_target_group"] = self.group_for_unit(state["target_unit"])
                row[f"lag{lag}_target_task"] = state["target_unit"] if self.ablation_unit == "task" else None
                row[f"lag{lag}_drop_rate"] = state["drop_rate"]

            with Path(self.log_path).open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")

    def group_for_unit(self, unit):
        if unit is None:
            return None
        if self.ablation_unit == "task":
            return self.task_to_group.get(str(unit), "unknown")
        return str(unit)

    def _advance_window(self):
        if self.consumed_in_window:
            self.history.append({
                "target_unit": self.target_unit,
                "drop_rate": self.drop_rate,
            })
        if not self.schedule:
            self._refill_schedule()
        self.target_unit, self.drop_rate = self.schedule.pop()
        self.consumed_in_window = 0
        self.kept = Counter()
        self.dropped = Counter()

    def _refill_schedule(self):
        treatments = [(unit, rate) for unit in self.units for rate in self.drop_rates]
        controls = max(1, round(len(treatments) * self.control_frac / max(1e-9, 1 - self.control_frac)))
        treatments.extend((None, 0.0) for _ in range(controls))
        self.rng.shuffle(treatments)
        self.schedule.extend(treatments)


def _load_group_map(path):
    path = Path(path)
    if not path.exists():
        repo_path = Path(__file__).resolve().parents[2] / path
        if repo_path.exists():
            path = repo_path
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if "task_to_group" in data:
        return {str(k): str(v) for k, v in data["task_to_group"].items()}
    if "groups" in data:
        data = data["groups"]
    task_to_group = {}
    for group, tasks in data.items():
        for task in tasks:
            task_to_group[str(task)] = str(group)
    return task_to_group


def _parse_drop_rates(raw):
    rates = [float(x.strip()) for x in str(raw).split(",") if x.strip()]
    if not rates:
        raise ValueError("--ablation_drop_rates must contain at least one numeric rate")
    for rate in rates:
        if rate < 0 or rate > 1:
            raise ValueError(f"Invalid ablation drop rate {rate}; expected 0 <= rate <= 1")
    return rates


def _window_steps_for_budget(args, units, drop_rates, eff_batch):
    explicit = int(getattr(args, "ablation_window_steps", 0) or 0)
    min_steps = max(1, int(getattr(args, "ablation_min_window_steps", 8)))
    max_steps = max(min_steps, int(getattr(args, "ablation_max_window_steps", explicit or 50)))
    if explicit > 0 and explicit != 50:
        return max(min_steps, min(max_steps, explicit))

    max_length = int(getattr(args, "max_length", 1024))
    token_budget = int(getattr(args, "token_budget", 0))
    aux_ratio = float(getattr(args, "aux_ratio", 0.0))
    total_steps = max(1, int(token_budget * (1 + aux_ratio) // max(1, max_length * eff_batch)))
    cells = max(1, len(units) * len(drop_rates))
    controls = max(1, round(cells * float(getattr(args, "ablation_control_frac", 0.2)) / max(1e-9, 1 - float(getattr(args, "ablation_control_frac", 0.2)))))
    target_windows = max(1.0, (cells + controls) * float(getattr(args, "ablation_target_passes", 1.5)))
    return max(min_steps, min(max_steps, round(total_steps / target_windows)))


def _aux_probability(aux_ratio):
    aux_ratio = float(aux_ratio)
    if aux_ratio <= 0:
        return 0.0
    return aux_ratio / (1.0 + aux_ratio)


def _get_task(ex):
    if isinstance(ex, dict):
        for key in ("task", "_task", "source_task"):
            value = ex.get(key)
            if value not in (None, ""):
                return value
    return None


def _pick_main_loss(metrics):
    for key in ("eval_main_loss", "eval/main_loss", "final_main_loss", "final/main_loss"):
        if key in metrics:
            return float(metrics[key])
    return None


def _clean_metric_fragment(value):
    return str(value).replace("/", "_").replace(" ", "_")


def _str_to_bool(value):
    if isinstance(value, bool):
        return value
    value = str(value).lower()
    if value in ("1", "true", "t", "yes", "y", "on"):
        return True
    if value in ("0", "false", "f", "no", "n", "off"):
        return False
    raise argparse.ArgumentTypeError(f"Expected boolean value, got {value!r}")
