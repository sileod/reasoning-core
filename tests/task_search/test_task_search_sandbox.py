import dataclasses
import json
import random
import time
import types
from pathlib import Path
import subprocess
import tempfile

import pytest

from reasoning_core.task_search import prior_audit, trajectory, validation

from reasoning_core.task_search.implementor_prompt import (
    PACE,
    _prior_audit_command,
    _sample_command,
    _sample_command_for,
    _selfcheck_command_for,
    render_implementor_prompt,
)
from reasoning_core.task_search.plan import (
    SearchPlan,
    Trial,
    _frozen_module_drift,
    _plan_problems,
    _select_trials,
    load_plan,
)
from reasoning_core.task_search.implementation_runner import (
    _mini_config,
    _prepare_harness,
    _retryable_harness_failure,
    generation_metadata,
    opencode_config,
    opencode_permissions,
)
from reasoning_core.task_search.sandbox import (
    _resource_command,
    _run_validation,
    _sandbox_command,
    _minimal_environment,
)
from reasoning_core.task_search.validation import (
    _outside_owned,
    _owned_digest,
    _review_source,
    _sample_review,
    _sample_sanity,
    _step_usage,
    _task_classes,
    _task_metadata,
    _undiscoverable,
    sample_shortfall,
)


ROOT = Path(__file__).parents[2]
PLAN = ROOT / "reasoning_core" / "task_search" / "plans" / "wave0.yaml"


# A prompt of realistic length, because the gate now measures prompt text as well as
# answers: a file of headings with nothing under them is not a worked example.
SAMPLE_PROMPT = (
    "Prompt:\nSort the multiset {3, 1, 2} and report the median as an"
    " integer. Show the sorted order first, then the element that sits"
    " in the middle of it.\n"
)
SAMPLE_BODY = "".join(
    f"# Level {level}\n" + (SAMPLE_PROMPT + f"Answer: {level}{index}\n") * 2
    for index, level in enumerate(("0", "2", "5"))
)

def test_bubblewrap_makes_only_owned_path_and_runtime_writable(tmp_path):
    # Strict sandboxes intentionally hide host /tmp, so place this integration
    # fixture on the same non-/tmp filesystem used by real task-search runs.
    with tempfile.TemporaryDirectory(prefix=".task-search-test-", dir=ROOT) as root:
        root = Path(root)
        worktree = root / "worktree"
        owned = worktree / "owned"
        runtime = root / "runtime"
        owned.mkdir(parents=True)
        (worktree / "sibling.txt").write_text("original\n")
        host_pid = __import__("os").getpid()
        with tempfile.NamedTemporaryFile(prefix="task-search-", dir="/tmp") as sentinel:
            command = _sandbox_command(
                [
                    "/bin/bash",
                    "-c",
                    "printf allowed > owned/result.txt; "
                    "if printf forbidden > sibling.txt 2>/dev/null; then exit 9; fi; "
                    f"test ! -e /proc/{host_pid}; "
                    f"test ! -e {sentinel.name}",
                ],
                worktree=worktree,
                owned_path="owned",
                runtime_root=runtime,
            )

            import subprocess

            subprocess.run(command, check=True)

        assert (owned / "result.txt").read_text() == "allowed"
        assert (worktree / "sibling.txt").read_text() == "original\n"

def test_bubblewrap_can_overlay_one_harness_runtime_file():
    with tempfile.TemporaryDirectory(prefix=".task-search-test-", dir=ROOT) as root:
        root = Path(root)
        worktree = root / "worktree"
        owned = worktree / "owned"
        runtime = root / "runtime"
        target = root / "harness-home" / "bin" / "helper"
        source = runtime / "helper"
        owned.mkdir(parents=True)
        target.parent.mkdir(parents=True)
        runtime.mkdir()
        target.write_text("host original\n")
        source.write_text("runtime original\n")
        command = _sandbox_command(
            ["/bin/bash", "-c", f"printf worker > {target}"],
            worktree=worktree,
            owned_path="owned",
            runtime_root=runtime,
            writable_overlays=((source, target),),
        )

        subprocess.run(command, check=True)

        assert source.read_text() == "worker"
        assert target.read_text() == "host original\n"

def test_systemd_resource_wrapper_records_hard_limits():
    command = _resource_command(
        ["bwrap", "true"],
        {
            "enabled": True,
            "executable": "/usr/bin/systemd-run",
            "memory_max": "8G",
            "tasks_max": 512,
            "cpu_quota": "400%",
        },
    )

    assert "MemoryMax=8G" in command
    assert "TasksMax=512" in command
    assert "CPUQuota=400%" in command
    assert command[-2:] == ["bwrap", "true"]

def test_independent_validation_times_out(tmp_path):
    with tempfile.TemporaryDirectory(prefix=".task-search-test-", dir=ROOT) as root:
        root = Path(root)
        worktree = root / "worktree"
        owned = worktree / "owned"
        owned.mkdir(parents=True)
        results = _run_validation(
            worktree,
            ("/bin/sleep 2",),
            root / "validation.log",
            owned_path="owned",
            runtime_root=root / "runtime",
            bwrap_bin="bwrap",
            resource_limits={"enabled": False},
            timeout_seconds=0.05,
        )

    assert results == [
        {
            "command": "/bin/sleep 2",
            "exit_code": 124,
            "timed_out": True,
        }
    ]

def test_environment_is_built_from_an_allowlist_not_subtracted_from(monkeypatch):
    """Inheriting the session is what leaked; naming what to drop can only ever lag it.

    The old sanitizer removed the credentials it was told about and passed on everything
    else -- which on this machine meant six other API keys, the ssh and dbus addresses of
    the host, and the config paths that had mini reading the operator's own dotfiles.
    """
    monkeypatch.setenv("PROVIDER_API_KEY", "secret")
    monkeypatch.setenv("UNRELATED_API_KEY", "other-secret")
    monkeypatch.setenv("SSH_CONNECTION", "10.0.0.1 22")
    monkeypatch.setenv("PATH", "/usr/bin")

    environment = _minimal_environment(("PROVIDER_API_KEY",))

    assert environment["PROVIDER_API_KEY"] == "secret"
    assert environment["PATH"] == "/usr/bin"
    # Not named, so not there -- and nobody had to think of it.
    assert "UNRELATED_API_KEY" not in environment
    assert "SSH_CONNECTION" not in environment
    # The worker sees a fixed identity rather than the operator's login.
    assert environment["USER"] == environment["LOGNAME"] == "task-search"


def test_validation_is_given_no_credential_at_all():
    """Candidate code is the one process here with no reason to reach a provider."""
    assert "PROVIDER_API_KEY" not in _minimal_environment()

def test_sandboxed_validation_does_not_receive_named_credential(monkeypatch):
    monkeypatch.setenv("PROVIDER_API_KEY", "secret")
    with tempfile.TemporaryDirectory(prefix=".task-search-test-", dir=ROOT) as root:
        root = Path(root)
        worktree = root / "worktree"
        (worktree / "owned").mkdir(parents=True)
        results = _run_validation(
            worktree,
            ('test -z "${PROVIDER_API_KEY+x}"',),
            root / "validation.log",
            owned_path="owned",
            runtime_root=root / "runtime",
            bwrap_bin="bwrap",
            resource_limits={"enabled": False},
            timeout_seconds=5,
            credential_env_names=("PROVIDER_API_KEY",),
        )

    assert results[0]["exit_code"] == 0


def test_the_worker_is_told_no_path_that_describes_this_machine(tmp_path):
    """Two runs of one trial on two machines should differ by the work, not the paths.

    The host checkout lives under somebody's home on a share named after a cluster, and a
    path handed to the worker reaches the model and then the trajectory. Here the worktree
    is always the same string and so is the scratch space, whatever they are outside.
    """
    worktree = tmp_path / "worktree"
    (worktree / "owned").mkdir(parents=True)
    runtime_root = tmp_path / "runtime"

    command = _sandbox_command(
        ["true"],
        worktree=worktree,
        owned_path="owned",
        runtime_root=runtime_root,
        bwrap_bin="bwrap",
    )

    pairs = list(zip(command, command[1:]))
    setenv = {name: value for flag, name in pairs for check, value in pairs
              if flag == "--setenv" and check == name}
    assert setenv["HOME"] == "/home/task-search"
    assert setenv["XDG_CONFIG_HOME"] == "/home/runtime/config"
    assert setenv["TASK_SEARCH_SPEC"] == "/home/runtime/trial_spec.json"
    assert ("--chdir", "/home/workspace") in pairs
    assert ("--hostname", "task-search") in pairs

    # Host paths appear only as bind sources, never as something the worker is handed.
    sources = {command[i + 1] for i, flag in enumerate(command)
               if flag in {"--bind", "--ro-bind"}}
    handed = [argument for i, argument in enumerate(command)
              if str(tmp_path) in argument and argument not in sources]
    assert handed == []


def test_agy_keeps_the_real_home_because_it_authenticates_through_it(tmp_path):
    """Stated in a test rather than discovered when an AGY wave lands nothing."""
    worktree = tmp_path / "worktree"
    (worktree / "owned").mkdir(parents=True)

    command = _sandbox_command(
        ["true"],
        worktree=worktree,
        owned_path="owned",
        runtime_root=tmp_path / "runtime",
        bwrap_bin="bwrap",
        synthetic_home=False,
    )

    assert "HOME" not in command
