from pathlib import Path

import pytest

from reasoning_core.task_search import cli


PLAN = Path(__file__).parents[2] / "reasoning_core/task_search/plans/wave0.yaml"


@pytest.mark.parametrize("flags, expected", [([], False), (["--snapshots"], True),
                                            (["--no-snapshots"], False)])
def test_run_forwards_snapshot_setting(monkeypatch, flags, expected):
    seen = {}

    def run(*args, **kwargs):
        seen.update(kwargs)
        return []

    monkeypatch.setattr(cli, "run_plan", run)
    cli.main(["run", str(PLAN), "--model", "unused", *flags])
    assert seen["snapshots"] is expected


def test_check_returns_failure_for_plan_problems(monkeypatch, capsys):
    monkeypatch.setattr(cli, "_plan_problems", lambda *args: ["missing parent module"])
    monkeypatch.setattr(cli, "_frozen_module_drift", lambda *args: None)
    with pytest.raises(SystemExit) as error:
        cli.main(["check", str(PLAN)])
    assert error.value.code == 1
    assert "PROBLEM: missing parent module" in capsys.readouterr().out


def test_run_prints_orchestration_error_reason(monkeypatch, capsys):
    monkeypatch.setattr(cli, "run_plan", lambda *args, **kwargs: [{
        "trial_id": "N1", "status": "orchestration_error", "error": "harness unavailable",
    }])
    with pytest.raises(SystemExit) as error:
        cli.main(["run", str(PLAN), "--model", "unused", "--trial", "N1"])
    assert error.value.code == 1
    assert "N1: harness unavailable" in capsys.readouterr().err


def test_a_checkpoint_can_be_written_twice_and_never_claims_the_archive(monkeypatch, tmp_path):
    """The archive path means "this brief is finished": the briefs driver skips a brief the
    moment one exists. Checkpointing onto it both crashed the second round and retired the
    brief with a half-made wave. Round-by-round state belongs beside the archive, not on it."""
    from reasoning_core.task_search import wave_proposer

    archive = tmp_path / "checkpointed.yaml"
    partial = archive.with_suffix(archive.suffix + ".partial")
    finished = {"name": "checkpointed", "proposals": [], "rejected": [],
                "objective": {"requested": 0, "complete": True}}

    def fake_propose_wave(repo_root, **kwargs):
        checkpoint = kwargs["checkpoint"]
        for round_index in (1, 2, 3):
            checkpoint({**finished, "round": round_index})
            assert partial.exists(), "a round went unrecorded"
            assert not archive.exists(), "an unfinished wave claimed the archive"
        return finished

    monkeypatch.setattr(wave_proposer, "propose_wave", fake_propose_wave)
    monkeypatch.setattr(cli, "build_pool", lambda *args, **kwargs: None)
    monkeypatch.setenv("FAKE_PROPOSER_KEY", "k")

    cli.main(["propose", "checkpointed", "--output", str(archive),
              "--count", "1", "--api-key-env", "FAKE_PROPOSER_KEY"])

    assert archive.exists(), "the finished wave was never archived"
    assert not partial.exists(), "the working file outlived the wave"
