"""LeanRunner against a fake REPL: timeouts and restarts must never shift or invent verdicts."""
import signal
import sys
import time

import pytest

from reasoning_core.runtime import TimeoutException
from reasoning_core.tasks import math_lean
from reasoning_core.template import Entry, Task

# Speaks the REPL protocol: one JSON command per blank-line-separated block. The import takes
# FAKE_IMPORT_S; a command containing "slow" takes 3 s; each reply echoes its command so a
# reply read by the wrong check is visible.
FAKE_REPL = r'''
import json, os, sys, time
block = []
for line in sys.stdin:
    if line.strip():
        block.append(line)
        continue
    if not block:
        continue
    cmd = json.loads("".join(block))["cmd"]
    block = []
    if cmd.startswith("import"):
        time.sleep(float(os.environ.get("FAKE_IMPORT_S", "0")))
    elif "slow" in cmd:
        time.sleep(3)
    severity = "error" if "bad" in cmd else "info"
    print(json.dumps({"env": 0, "messages": [{"severity": severity, "data": cmd}]}), flush=True)
'''


@pytest.fixture
def fake_repl(tmp_path, monkeypatch):
    (tmp_path / "repl.py").write_text(FAKE_REPL)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    lake = bin_dir / "lake"
    lake.write_text(f'#!/bin/sh\nexec {sys.executable} {tmp_path / "repl.py"}\n')  # `lake env <repl>`
    lake.chmod(0o755)
    monkeypatch.setattr(math_lean, "_ELAN_HOME", tmp_path)
    monkeypatch.setattr(math_lean, "_project", lambda use_mathlib=True: tmp_path)
    monkeypatch.setattr(math_lean, "_ensure_project", lambda use_mathlib=True: tmp_path / "repl")
    monkeypatch.setattr(math_lean, "_GLOBAL_RUNNERS", {})
    return monkeypatch


def _alarm_in(seconds):
    def handler(signum, frame):
        raise TimeoutException()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)


def test_an_interrupted_check_raises_and_the_next_check_gets_its_own_reply(fake_repl):
    runner = math_lean.LeanRunner()
    _alarm_in(1)
    try:
        with pytest.raises(TimeoutException):
            runner.check("slow proof")
    finally:
        signal.alarm(0)
    assert runner.proc is None
    assert "slow proof" not in runner.cache  # no verdict was recorded
    assert runner.check("next proof") == (True, "next proof")
    assert runner.check("bad proof") == (False, "bad proof")


def test_a_dead_repl_is_replaced_without_a_verdict(fake_repl):
    runner = math_lean.LeanRunner()
    runner.proc.kill()
    runner.proc.wait()
    assert runner.check("a proof") == (True, "a proof")


def test_the_repl_starts_outside_the_example_timeout(fake_repl):
    fake_repl.setenv("FAKE_IMPORT_S", "2")

    class Checked(Task):
        def prepare(self):
            math_lean.get_runner()

        def generate_entry(self):
            code = f"proof {time.time()}"
            return Entry({"code": code}, str(math_lean.get_runner().check(code)[0]))

        def render_prompt(self, metadata):
            return metadata["code"]

    entry = Checked(timeout=1).generate_example(max_tokens=0, timeout=1)
    assert entry.answer == "True"
    assert len(math_lean._GLOBAL_RUNNERS) == 1
