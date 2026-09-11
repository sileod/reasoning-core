"""The brief driver's judgement about what is a failure and what is a closed door."""
import argparse
import subprocess
import importlib.util
from pathlib import Path

import pytest


def _driver():
    path = Path(__file__).parents[2] / "scripts" / "propose_from_briefs.py"
    spec = importlib.util.spec_from_file_location("propose_from_briefs", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


driver = _driver()


class Completed:
    def __init__(self, returncode):
        self.returncode = returncode


def _arguments(**overrides):
    return argparse.Namespace(**{"cooldowns": 2, "cooldown_seconds": 60, **overrides})


@pytest.mark.parametrize("text, expected", [
    ("requests.exceptions.HTTPError: 429 Client Error: Too Many Requests", True),
    ('{"status":429,"title":"Too Many Requests"}', True),
    ("json.decoder.JSONDecodeError: Unterminated string", False),
    ("INCOMPLETE: requested 12", False),
    # A count that merely contains the digits is not a status code.
    ("accepted 1429 candidates", False),
])
def test_only_a_refusing_provider_reads_as_rate_limited(tmp_path, text, expected):
    log = tmp_path / "wave.log"
    log.write_text(text)
    assert driver.rate_limited(log) is expected


def test_a_missing_log_is_not_a_rate_limit(tmp_path):
    assert driver.rate_limited(tmp_path / "absent.log") is False


def test_a_wave_is_retried_after_the_provider_reopens(tmp_path, monkeypatch):
    """The block that prompted this refused a two-token request as fast as a wave."""
    log = tmp_path / "wave.log"
    outcomes = iter([(1, "429 Too Many Requests"), (0, "wrote the archive")])

    def run(command, cwd, stdout, stderr):
        code, text = next(outcomes)
        stdout.write(text)
        return Completed(code)

    slept = []
    monkeypatch.setattr(driver.subprocess, "run", run)
    monkeypatch.setattr(driver.time, "sleep", slept.append)

    completed, _, _ = driver.run_wave(_arguments(), ["cmd"], log)
    assert completed.returncode == 0
    assert slept == [60]


def test_waiting_is_bounded_so_a_closed_door_cannot_hold_the_job_open(tmp_path, monkeypatch):
    log = tmp_path / "wave.log"

    def run(command, cwd, stdout, stderr):
        stdout.write("429 Too Many Requests")
        return Completed(1)

    slept = []
    monkeypatch.setattr(driver.subprocess, "run", run)
    monkeypatch.setattr(driver.time, "sleep", slept.append)

    completed, _, _ = driver.run_wave(_arguments(cooldowns=2), ["cmd"], log)
    assert completed.returncode == 1
    assert slept == [60, 60]


def test_a_failure_that_is_not_a_rate_limit_returns_at_once(tmp_path, monkeypatch):
    log = tmp_path / "wave.log"

    def run(command, cwd, stdout, stderr):
        stdout.write("Traceback: something else went wrong")
        return Completed(1)

    slept = []
    monkeypatch.setattr(driver.subprocess, "run", run)
    monkeypatch.setattr(driver.time, "sleep", slept.append)

    completed, _, _ = driver.run_wave(_arguments(), ["cmd"], log)
    assert completed.returncode == 1 and slept == []


def test_the_shared_instruction_is_optional():
    with_shared = dict(driver.briefs(True))
    without = dict(driver.briefs(False))
    assert len(with_shared) == len(without) == 43
    slug = "compositional-generalization"
    assert without[slug] in with_shared[slug]
    assert len(with_shared[slug]) > len(without[slug])


def test_a_quota_block_does_not_spend_the_give_up_budget(tmp_path, monkeypatch, capsys):
    """A closed door is not a bad brief. Counting it stopped the driver for the night with
    thirty-seven briefs still owed, on waves that could not have succeeded."""
    calls = []

    def blocked(arguments, command, log_path):
        calls.append(command)
        log_path.write_text("429 Too Many Requests")
        return subprocess.CompletedProcess(command, 1), 6.0, True

    monkeypatch.setattr(driver, "run_wave", blocked)
    monkeypatch.setattr(driver.time, "sleep", lambda _: None)
    arguments = _arguments(log_dir=tmp_path, pause_seconds=0, prefix="k3",
                           count=12, rounds=3, model="", api_key_env="", dry_run=False)
    briefs = [(f"brief{index}", f"text {index}")
              for index in range(driver.GIVE_UP_AFTER + 2)]

    assert driver.sweep_once(arguments, briefs) is None
    assert len(calls) == len(briefs), "a blocked wave must not stop the sweep"
    assert "not counted" in capsys.readouterr().out
