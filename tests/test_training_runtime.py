from types import SimpleNamespace

import pytest

from reasoning_core.training.checkpointing import (
    COMPLETE_MARKER,
    ResumableCheckpointCallback,
    latest_complete_checkpoint,
    prepare_checkpoint_dir,
)
from reasoning_core.training.paths import HOME, home_path
from reasoning_core.training.dev_engine import format_qa, optimizer_eval_mode


def test_write_paths_must_stay_under_home(tmp_path):
    assert home_path(HOME / "runs") == HOME / "runs"
    outside = tmp_path if HOME not in tmp_path.parents else HOME.parent / "outside"
    with pytest.raises(ValueError):
        home_path(outside)


def test_only_complete_checkpoint_is_resumable(tmp_path):
    (tmp_path / "checkpoint-20").mkdir()
    complete = tmp_path / "checkpoint-10"
    complete.mkdir()
    (complete / COMPLETE_MARKER).touch()
    assert latest_complete_checkpoint(tmp_path) == str(complete)


def test_existing_trainer_checkpoint_is_adopted(tmp_path):
    checkpoint = tmp_path / "checkpoint-3"
    checkpoint.mkdir()
    for name in ("model.safetensors", "trainer_state.json", "optimizer.pt", "scheduler.pt"):
        (checkpoint / name).touch()
    prepare_checkpoint_dir(tmp_path)
    assert latest_complete_checkpoint(tmp_path) == str(checkpoint)


def test_wall_clock_checkpoint_marks_completed_save(tmp_path, monkeypatch):
    clock = iter((0.0, 61.0))
    monkeypatch.setattr("reasoning_core.training.checkpointing.time.monotonic", lambda: next(clock))
    callback = ResumableCheckpointCallback(every_minutes=1, stop_signals=())
    args = SimpleNamespace(output_dir=str(tmp_path))
    state = SimpleNamespace(global_step=7)
    control = SimpleNamespace(should_save=False, should_training_stop=False)

    callback.on_train_begin(args, state, control)
    callback.on_step_end(args, state, control)
    assert control.should_save
    (tmp_path / "checkpoint-7").mkdir()
    callback.on_save(args, state, control)
    assert (tmp_path / "checkpoint-7" / COMPLETE_MARKER).exists()


def test_signal_save_stops_without_implying_completion(tmp_path):
    callback = ResumableCheckpointCallback(every_minutes=0, stop_signals=())
    args = SimpleNamespace(output_dir=str(tmp_path))
    state = SimpleNamespace(global_step=9)
    control = SimpleNamespace(should_save=False, should_training_stop=False)
    callback.on_train_begin(args, state, control)
    callback._request_stop(None, None)
    callback.on_step_end(args, state, control)
    (tmp_path / "checkpoint-9").mkdir()
    callback.on_save(args, state, control)
    assert callback.interrupted
    assert control.should_training_stop


def test_short_arm_can_skip_forced_final_checkpoint(tmp_path):
    callback = ResumableCheckpointCallback(every_minutes=60, save_final=False, stop_signals=())
    args = SimpleNamespace(output_dir=str(tmp_path))
    state = SimpleNamespace(global_step=1, max_steps=1)
    control = SimpleNamespace(should_save=True, should_training_stop=True)
    callback.on_train_begin(args, state, control)
    callback.on_step_end(args, state, control)
    assert not control.should_save


def test_dev_formatter_matches_run_sft_contract():
    assert format_qa("1 + 1?", "2", "</s>") == {
        "prompt": "Q: 1 + 1?\nA:",
        "completion": " 2</s>",
    }


def test_optimizer_eval_mode_restores_prior_mode():
    calls = []
    inner = SimpleNamespace(param_groups=[{"train_mode": True}])
    optimizer = SimpleNamespace(
        optimizer=inner,
        eval=lambda: calls.append("eval"),
        train=lambda: calls.append("train"),
    )
    with optimizer_eval_mode(optimizer):
        calls.append("body")
    assert calls == ["eval", "body", "train"]
