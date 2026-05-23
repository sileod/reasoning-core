import json
import random

from reasoning_core.training.mix_ablation import MixAblationTracker


def _tracker(log_path):
    tracker = MixAblationTracker(
        tasks=["a", "b"],
        task_ratios=[0.0, 5.0],
        window_aux_examples=2,
        window_steps=2,
        tasks_per_window=(1,),
        control_frac=0.0,
        seed=0,
        aux_ratio=0.5,
        log_path=str(log_path),
        wandb_analysis=False,
    )
    tracker.active_task_ratios = {"a": 0.0}
    tracker.max_active_ratio = 1.0
    return tracker


def test_sync_mode_advances_on_eval_not_aux_count(tmp_path):
    tracker = _tracker(tmp_path / "mix.jsonl")
    tracker.sync_windows_to_eval(eval_steps=10, eff_batch=4)
    rng = random.Random(0)

    for _ in range(4):
        tracker.should_drop("b", rng)

    assert tracker.active_task_ratios == {"a": 0.0}
    assert not tracker.history
    tracker.write_eval_row(step=10, eval_main_loss=1.0, eval_main_loss_delta=None)

    row = json.loads((tmp_path / "mix.jsonl").read_text())
    assert row["active_task_ratios"] == {"a": 0.0}
    assert tracker.history[-1]["active_task_ratios"] == {"a": 0.0}


def test_unsynced_mode_still_advances_on_aux_count(tmp_path):
    tracker = _tracker(tmp_path / "mix.jsonl")
    rng = random.Random(0)

    for _ in range(3):
        tracker.should_drop("b", rng)

    assert tracker.history[-1]["active_task_ratios"] == {"a": 0.0}
