import argparse
import hashlib
import json
import random
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

from appdirs import user_log_dir
from datasets import IterableDataset
from transformers import TrainerCallback


__all__ = [
    "add_mix_ablation_args",
    "wrap_aux_dataset_with_ablation",
    "MixAblationCallback",
]


DEFAULT_RC_TASKS = (
    "arithmetics", "bayesian_association", "bayesian_intervention", "binding",
    "causal_reasoning", "code_diff", "code_execution", "code_program_synthesis",
    "conjecture_entailment", "constrained_continuation", "constraint_satisfaction",
    "continuation", "coreference", "count_elements", "diff_patching",
    "diff_prediction", "equation_system", "evidence_retrieval", "formal_maths",
    "grammar", "graph_dependencies", "graph_isomorphism", "graph_operations",
    "graph_pathfinding", "graph_successors", "knowledge", "lambda_reduction",
    "lexical_knowledge", "locate_error", "logic", "logic_formalization",
    "logic_nli", "navigation", "parsability", "parsing", "planning",
    "proof_reconstruction", "qstr", "qualitative_reasoning", "reference_tracking",
    "regex", "regex_following", "regex_induction", "regex_reasoning",
    "sequential_induction", "set_equality", "set_intersection",
    "set_missing_element", "set_operations", "table_conversion", "table_qa",
    "term_unification", "tracking",
)


def add_mix_ablation_args(parser):
    parser.add_argument("--mix_ablation", type=_str_to_bool, nargs="?", const=True, default=True)
    parser.add_argument("--ablation_tasks", type=str, default=",".join(DEFAULT_RC_TASKS))
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
    tasks = _parse_tasks(args.ablation_tasks)
    drop_rates = _parse_drop_rates(args.ablation_drop_rates)
    window_steps = _window_steps_for_budget(args, tasks, drop_rates, eff_batch)
    window_aux_examples = max(
        1,
        round(window_steps * int(eff_batch) * _aux_probability(getattr(args, "aux_ratio", 0.0))),
    )

    tracker = MixAblationTracker(
        tasks=tasks,
        drop_rates=drop_rates,
        window_aux_examples=window_aux_examples,
        window_steps=window_steps,
        control_frac=float(args.ablation_control_frac),
        seed=int(getattr(args, "seed", 0)),
        aux_ratio=float(getattr(args, "aux_ratio", 0.0)),
        log_path=_resolve_log_path(args),
        wandb_analysis=(
            bool(getattr(args, "ablation_wandb_analysis", True))
            and bool(getattr(args, "ablation_compute_ratios", True))
        ),
        analysis_min_rows=int(getattr(args, "ablation_analysis_min_rows", 30)),
        analysis_every_rows=int(getattr(args, "ablation_analysis_every_rows", 5)),
        analysis_step_df=int(getattr(args, "ablation_analysis_step_df", 2)),
    )

    def gen():
        rng = random.Random(int(getattr(args, "seed", 0)) + 1729)
        for ex in aux_ds:
            task = _get_task(ex)
            if tracker.should_drop(task, rng):
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

        delta = None if self.previous_loss is None else loss - self.previous_loss
        self.previous_loss = loss
        self.last_logged_step = state.global_step
        self.tracker.write_eval_row(int(state.global_step), loss, delta)
        self.eval_rows += 1
        self._maybe_log_wandb_analysis(step=int(state.global_step))

    def _maybe_log_wandb_analysis(self, step):
        if not self.tracker.wandb_analysis:
            return
        if self.eval_rows < self.tracker.analysis_min_rows:
            return
        if self.eval_rows % max(1, self.tracker.analysis_every_rows):
            return

        try:
            import wandb

            if wandb.run is None:
                return
            from reasoning_core.training.analyze_mix_ablation import analyze_log_path

            result = analyze_log_path(self.tracker.log_path, step_df=self.tracker.analysis_step_df)
            metrics = {"mix_ablation/analysis_rows": int(self.eval_rows)}
            for row in result.to_dict(orient="records"):
                task = _clean_metric_fragment(row["task"])
                metrics[f"mix_ablation/best_drop_rate/{task}"] = float(row["best_drop_rate"])
                metrics[f"mix_ablation/recommended_keep_ratio/{task}"] = float(row["recommended_keep_ratio"])
                metrics[f"mix_ablation/stderr/{task}"] = float(row["stderr"])
                metrics[f"mix_ablation/effect/{task}"] = float(row["effect"])
            wandb.log(metrics, step=step)
        except Exception as exc:
            if not self.analysis_warning_printed:
                print(f"mix_ablation W&B analysis disabled after error: {exc}")
                self.analysis_warning_printed = True


@dataclass
class MixAblationTracker:
    tasks: list
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
    analysis_step_df: int = 2
    lock: Lock = field(default_factory=Lock)
    consumed_in_window: int = 0
    target_task: str | None = None
    drop_rate: float = 0.0
    kept: Counter = field(default_factory=Counter)
    dropped: Counter = field(default_factory=Counter)
    history: deque = field(default_factory=lambda: deque(maxlen=3))

    def __post_init__(self):
        self.rng = random.Random(self.seed + 104729)
        self.task_set = set(self.tasks)
        self.schedule = []
        self._refill_schedule()
        self._advance_window()
        Path(self.log_path).parent.mkdir(parents=True, exist_ok=True)

    def should_drop(self, task, rng):
        task = task if task in self.task_set else "unknown"
        with self.lock:
            if self.consumed_in_window >= self.window_aux_examples:
                self._advance_window()
            self.consumed_in_window += 1
            should_drop = self.target_task is not None and task == self.target_task and rng.random() < self.drop_rate
            (self.dropped if should_drop else self.kept)[task] += 1
            return should_drop

    def write_eval_row(self, step, eval_main_loss, eval_main_loss_delta):
        with self.lock:
            row = {
                "step": step,
                "target_task": self.target_task,
                "drop_rate": self.drop_rate,
                "eval_main_loss": eval_main_loss,
                "eval_main_loss_delta": eval_main_loss_delta,
                "aux_ratio": self.aux_ratio,
                "window_aux_examples": self.window_aux_examples,
                "window_steps": self.window_steps,
            }
            for task, count in sorted(self.kept.items()):
                row[f"kept_task/{task}"] = count
            for task, count in sorted(self.dropped.items()):
                row[f"dropped_task/{task}"] = count
            for lag, state in enumerate(reversed(list(self.history)[-3:]), start=1):
                row[f"lag{lag}_target_task"] = state["target_task"]
                row[f"lag{lag}_drop_rate"] = state["drop_rate"]

            with Path(self.log_path).open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, sort_keys=True) + "\n")

    def _advance_window(self):
        if self.consumed_in_window:
            self.history.append({"target_task": self.target_task, "drop_rate": self.drop_rate})
        if not self.schedule:
            self._refill_schedule()
        self.target_task, self.drop_rate = self.schedule.pop()
        self.consumed_in_window = 0
        self.kept = Counter()
        self.dropped = Counter()

    def _refill_schedule(self):
        treatments = [(task, rate) for task in self.tasks for rate in self.drop_rates]
        controls = max(1, round(len(treatments) * self.control_frac / max(1e-9, 1 - self.control_frac)))
        treatments.extend((None, 0.0) for _ in range(controls))
        self.rng.shuffle(treatments)
        self.schedule.extend(treatments)


def _parse_tasks(raw):
    tasks = sorted({x.strip() for x in str(raw).split(",") if x.strip()})
    if not tasks:
        raise ValueError("--ablation_tasks must contain at least one task")
    return tasks


def _parse_drop_rates(raw):
    rates = [float(x.strip()) for x in str(raw).split(",") if x.strip()]
    if not rates:
        raise ValueError("--ablation_drop_rates must contain at least one numeric rate")
    for rate in rates:
        if rate < 0 or rate > 1:
            raise ValueError(f"Invalid ablation drop rate {rate}; expected 0 <= rate <= 1")
    return rates


def _resolve_log_path(args):
    if args.ablation_log_path:
        return args.ablation_log_path
    keys = (
        "model_name", "main_data", "aux_data", "aux_ratio", "token_budget",
        "max_length", "seed", "script_version", "ablation_drop_rates",
        "ablation_control_frac",
    )
    payload = {key: str(getattr(args, key, "")) for key in keys}
    run_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
    return str(Path(user_log_dir("reasoning-core")) / "taskmix" / f"{run_id}.jsonl")


def _window_steps_for_budget(args, tasks, drop_rates, eff_batch):
    explicit = int(getattr(args, "ablation_window_steps", 0) or 0)
    min_steps = max(1, int(getattr(args, "ablation_min_window_steps", 8)))
    max_steps = max(min_steps, int(getattr(args, "ablation_max_window_steps", explicit or 50)))
    if explicit > 0 and explicit != 50:
        return max(min_steps, min(max_steps, explicit))

    max_length = int(getattr(args, "max_length", 1024))
    token_budget = int(getattr(args, "token_budget", 0))
    aux_ratio = float(getattr(args, "aux_ratio", 0.0))
    total_steps = max(1, int(token_budget * (1 + aux_ratio) // max(1, max_length * eff_batch)))
    cells = max(1, len(tasks) * len(drop_rates))
    control_frac = float(getattr(args, "ablation_control_frac", 0.2))
    controls = max(1, round(cells * control_frac / max(1e-9, 1 - control_frac)))
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
                return str(value)
    return "unknown"


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
