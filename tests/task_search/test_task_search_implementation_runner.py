import dataclasses
import os
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
    _RETRY_CEILING_SECONDS,
    _retry_delay,
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

def test_opencode_profile_leaves_write_scope_to_mount_sandbox():
    trial = load_plan(PLAN).trials[0]
    config = opencode_config(trial, "task-search-worker")
    permissions = config["agent"]["task-search-worker"]["permission"]

    assert permissions["edit"] == "allow"
    assert permissions["bash"]["*"] == "deny"
    assert permissions["bash"][trial.validation[0]] == "allow"
    assert permissions["task"] == "deny"


def test_snapshots_toggle_does_not_change_worker_permissions():
    trial = load_plan(PLAN).trials[0]
    disabled = opencode_config(trial, "worker")
    enabled = opencode_config(trial, "worker", snapshots=True)
    assert disabled.pop("snapshot") is False
    assert enabled.pop("snapshot") is True
    assert disabled == enabled


@pytest.mark.parametrize("runs_root", ["/tmp/task-search-test", "/run/task-search-test"])
def test_hidden_run_directory_fails_before_worktree_or_harness_setup(monkeypatch, runs_root):
    from reasoning_core.task_search import implementation_runner as runner

    def unexpected(*args, **kwargs):
        pytest.fail("invalid run directory reached subprocess setup")

    monkeypatch.setattr(runner.subprocess, "check_output", unexpected)
    with pytest.raises(ValueError, match="runs root cannot be under"):
        runner.run_plan(PLAN, repo_root=ROOT, model="unused", runs_root=runs_root)

def test_generation_metadata_records_requested_but_unforwarded_seed():
    metadata = generation_metadata(
        "example-provider/example-model",
        "1.18.20",
        "task-search-worker",
        requested_seed=42,
    )

    assert metadata["provider_name"] == "example-provider"
    assert metadata["settings"]["requested_seed"] == 42
    assert metadata["settings"]["seed_forwarded"] is False

def test_generation_metadata_records_selected_harness():
    metadata = generation_metadata(
        "example-model",
        "1.15.0",
        "mini-default",
        provider_name="provider-cli",
        harness_name="mini",
    )

    assert metadata["harness_name"] == "mini"
    assert metadata["provider_name"] == "provider-cli"

def test_opencode_profile_forwards_seed_when_requested():
    trial = load_plan(PLAN).trials[0]
    config = opencode_config(
        trial,
        "task-search-worker",
        requested_seed=123,
        forward_seed=True,
        max_steps=17,
    )

    assert config["agent"]["task-search-worker"]["seed"] == 123
    assert config["agent"]["task-search-worker"]["steps"] == 17

def test_hlink_is_the_only_harness_launcher(tmp_path):
    command = _prepare_harness(
        "hlink",
        "opencode",
        worktree=tmp_path,
        prompt="assignment",
        model="example-model",
        provider="nim",
        agent="worker",
        variant=None,
        config_path=None,
        trajectory_path=None,
        timeout_seconds=90,
        agy_log_path=tmp_path / "agy.log",
    )

    assert command[:2] == ["hlink", "opencode"]
    assert command[command.index("-C") + 1] == str(tmp_path)
    assert command[command.index("-p") + 1] == "assignment"
    assert command[command.index("--provider") + 1] == "nim"
    assert command[command.index("--") + 1 :] == [
        "--pure",
        "--agent",
        "worker",
        "--format",
        "json",
    ]

def test_retry_classifier_accepts_explicit_provider_transients_only(tmp_path):
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps(
            {
                "type": "error",
                "error": {
                    "name": "APIError",
                    "data": {"statusCode": 429, "isRetryable": True},
                },
            }
        )
        + "\n"
    )
    transient = {
        "status": "harness_failed",
        "harness_exit_code": 1,
        "harness_log": str(events),
    }

    assert _retryable_harness_failure(transient) == "provider_429"
    assert (
        _retryable_harness_failure({**transient, "status": "validation_failed"}) is None
    )
    events.write_text(
        json.dumps(
            {
                "type": "error",
                "error": {
                    "name": "ConfigurationError",
                    "data": {"statusCode": 400, "isRetryable": False},
                },
            }
        )
        + "\n"
    )
    assert _retryable_harness_failure(transient) is None
    assert (
        _retryable_harness_failure(
            {"status": "harness_failed", "harness_exit_code": -15}
        )
        == "signal_15"
    )


def test_a_provider_backoff_grows_past_one_minute_and_is_jittered():
    """wave8 burned 120 attempts retrying a shared token bucket in lockstep.

    The delay used to be capped at 60s, which against a per-minute limit meant every
    worker woke into the same saturated minute, every time. Growth is what eventually
    outlasts the bucket; jitter is what stops the herd re-arriving together.
    """
    third = [_retry_delay(60, 3) for _ in range(50)]
    assert min(third) > 60, "the delay must be able to outgrow a one-minute window"
    assert len(set(third)) > 1, "an unjittered delay retries the whole wave in lockstep"
    assert max(third) <= _RETRY_CEILING_SECONDS * 1.5

    assert all(_retry_delay(30, 9) <= _RETRY_CEILING_SECONDS * 1.5 for _ in range(20))
    assert sum(_retry_delay(60, 1) for _ in range(400)) / 400 == pytest.approx(60, rel=0.2)


def test_mini_is_driven_by_text_because_the_workers_have_no_tool_calling(tmp_path):
    """mini's default config talks to the model in tool calls, which the workers cannot make.

    ALBERT's deepseek-v4-flash answers a `tools` request with two characters of content and
    a null tool_calls, at any output budget, so mini's tool-calling loop never reaches step
    one: eight trials, three API calls each, no assistant content, RepeatedFormatError,
    `no_implementation` across the board. opencode is unaffected -- it does not drive the
    worker through native tool calls -- which is why it scored 4/8 on the same eight
    trials, on the same model, on the same commit.

    The config alone was not enough: it carries prompts, while the parser is chosen by the
    model class, which defaults to the tool-calling one. Asking for a fenced block and then
    sending a `tools` request is what produced "found 0 actions" on a prompt the model
    answers correctly by hand. Both halves have to move together, so both are pinned here.
    """
    def command_for(harness):
        return _prepare_harness(
            "hlink", harness,
            worktree=tmp_path / "worktree",
            prompt="do the thing",
            model="deepseek-v4-flash",
            provider="albert",
            agent="task-search-worker",
            variant=None,
            config_path=tmp_path / "config.yaml",
            trajectory_path=tmp_path / "trajectory.json",
            timeout_seconds=1800,
            agy_log_path=tmp_path / "agy.log",
        )

    mini = command_for("mini")
    assert "mini_textbased.yaml" in mini
    assert "mini.yaml" not in mini
    assert _mini_config(
        max_steps=40, timeout_seconds=1800,
    )["model"]["model_class"] == "litellm_textbased"

    # The other harnesses do not get dragged along by the change.
    assert "mini_textbased.yaml" not in command_for("opencode")


def test_a_pass_retires_only_a_bounded_number_of_spent_runs(tmp_path, monkeypatch):
    """Deleting one run directory is a recursive unlink of a worktree over NFS and takes
    minutes. Uncapped, a first pass facing a year of them stalls the service for an hour
    before it plans anything, and the poll interval stops meaning what it says."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_implementors", Path(__file__).parents[2] / "scripts" / "run_implementors.py")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)

    runs = tmp_path / "runs"
    for index in range(driver.RETIRE_PER_PASS + 3):
        directory = runs / "wave1" / f"2026010{index}T000000Z"
        directory.mkdir(parents=True)
        os.utime(directory, (0, index))
    monkeypatch.setattr(driver, "RUNS", runs)

    spent = driver.retire_runs(7, apply=False, limit=driver.RETIRE_PER_PASS)

    assert len(spent) == driver.RETIRE_PER_PASS
    assert [directory.name for directory in spent] == sorted(
        directory.name for directory in spent), "the oldest runs must go first"


def test_the_retry_ladder_reaches_the_ceiling_it_documents(monkeypatch):
    """`_RETRY_CEILING_SECONDS` is ten minutes because a provider 429 is one bucket shared
    by the whole wave and the wait has to outlast its refill window. A budget of two never
    climbed past about ninety seconds, so every retry woke into the same saturated minute
    and the ceiling described a regime the runner could not reach."""
    from reasoning_core.task_search.implementation_runner import (
        DEFAULT_TRANSIENT_RETRIES,
        _RETRY_CEILING_SECONDS,
        _retry_delay,
    )

    monkeypatch.setattr(random, "uniform", lambda low, high: 1.0)
    ladder = [_retry_delay(30, attempt)
              for attempt in range(1, DEFAULT_TRANSIENT_RETRIES + 1)]

    assert ladder == sorted(ladder), "the wait must grow with each refusal"
    assert max(ladder) >= 240, (
        f"the last rung waits {max(ladder)}s, which is inside a per-minute quota window")
    assert sum(ladder) < _RETRY_CEILING_SECONDS + 1800, (
        "waiting must stay small beside the trials it protects")


def test_an_empty_backlog_says_whether_it_is_finished_or_stuck(tmp_path, monkeypatch):
    """`0 proposals owed` was printed four times an hour for six days while the archive
    held ninety unimplemented proposals: every one of them had been counted out of budget
    by plan trials that never ran. The line an idle pipeline prints and the line a blind
    one prints have to be different sentences, or the stall is invisible."""
    import importlib.util
    from types import SimpleNamespace

    spec = importlib.util.spec_from_file_location(
        "run_implementors", Path(__file__).parents[2] / "scripts" / "run_implementors.py")
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)

    held_back = [SimpleNamespace(name=f"idea_{index}") for index in range(90)]
    monkeypatch.setattr(driver, "pending", lambda root, **kwargs: list(held_back))

    stuck = driver.why_nothing_is_owed(SimpleNamespace(max_attempts=3))
    assert "90" in stuck and "--max-attempts 3" in stuck
    assert "outcomes" in stuck, "the sentence must say where to look"

    # Without a cap nothing can be held back by one, so the quiet reading is the true one.
    assert "no attempt cap" in driver.why_nothing_is_owed(SimpleNamespace(max_attempts=0))

    monkeypatch.setattr(driver, "pending", lambda root, **kwargs: [])
    assert driver.why_nothing_is_owed(
        SimpleNamespace(max_attempts=3)) == "0 proposals owed: every archived proposal has a task"


def test_a_second_provider_answers_what_the_first_one_refuses(tmp_path):
    """A 429 is one bucket shared by every worker in the wave, so a provider that goes
    down does not cost one trial, it costs the wave. The retry ladder waits ten minutes
    and then gives up; a fallback keeps the run moving instead. It answers on its own
    default model, which is the price, so the launch also asks to be told when the route
    changes -- into this trial's stderr, since the status file Harness Link writes is one
    per provider and every concurrent trial shares it."""
    from reasoning_core.task_search.implementation_runner import _launcher, _routes_taken

    command = _prepare_harness(
        "hlink", "opencode",
        worktree=tmp_path, prompt="assignment", model="deepseek-v4-flash",
        provider="albert", fallback="inferx", agent="worker", variant=None,
        config_path=None, trajectory_path=None, timeout_seconds=90,
        agy_log_path=tmp_path / "agy.log",
    )

    assert command[command.index("--fallback") + 1] == "inferx"
    assert "--show-routing" in command
    assert command.index("--fallback") < command.index("--"), (
        "the flag belongs to Harness Link, not to the harness it launches")

    stderr = tmp_path / "stderr.log"
    stderr.write_text("albert: fallback enabled\n"
                      "[hlink] primary -> albert/deepseek-v4-flash\n"
                      "[hlink] fallback -> inferx/deepseek-v4.1-flash\n"
                      "[hlink] fallback -> inferx/deepseek-v4.1-flash\n")

    assert _routes_taken(stderr) == [
        {"label": "primary", "route": "albert/deepseek-v4-flash"},
        {"label": "fallback", "route": "inferx/deepseek-v4.1-flash"},
    ]
    assert _launcher("0.3.0", "inferx", stderr)["fallback"]["provider"] == "inferx"
    # Absent, not empty, when no fallback was armed: a run.json without the key is a run
    # that could only have been served by the provider it names.
    assert "fallback" not in _launcher("0.3.0", None)


def test_a_trial_says_it_was_allowed_to_answer_from_somewhere_else(tmp_path):
    """`provider_name` is provenance, and with a fallback armed it means "this one, or
    the other one where it refused". The task file keeps that admission, because the
    metadata is written into the prompt before the run and cannot learn afterwards which
    of the two actually served."""
    from reasoning_core.task_search.implementation_runner import generation_metadata

    armed = generation_metadata("deepseek-v4-flash", "0.3.0", "worker",
                                provider_name="albert", fallback_provider_name="inferx")
    alone = generation_metadata("deepseek-v4-flash", "0.3.0", "worker",
                                provider_name="albert")

    assert armed["provider_name"] == "albert"
    assert armed["settings"]["fallback_provider"] == "inferx"
    assert "fallback_provider" not in alone["settings"]


def test_a_fallback_without_its_own_key_is_refused_before_the_wave_runs(tmp_path, monkeypatch):
    """The worker's environment is an allowlist. A fallback provider reads a key of its
    own, and unnamed it is simply absent, so Harness Link exits before the first step of
    every trial -- the whole wave lost to the switch that was meant to save it. One
    refusal at the top costs nothing and says what is missing."""
    from reasoning_core.task_search import cli

    monkeypatch.setenv("ALBERT_API_KEY", "x")
    monkeypatch.delenv("INFERX_API_KEY", raising=False)
    monkeypatch.delenv("TASK_SEARCH_KEY_ENV", raising=False)

    with pytest.raises(SystemExit) as refusal:
        cli.main(["run", str(tmp_path / "plan.yaml"), "--fallback", "inferx",
                  "--credential-env", "ALBERT_API_KEY"])
    assert "--credential-env" in str(refusal.value)

    with pytest.raises(SystemExit) as unset:
        cli.main(["run", str(tmp_path / "plan.yaml"), "--fallback", "inferx",
                  "--credential-env", "ALBERT_API_KEY",
                  "--credential-env", "INFERX_API_KEY"])
    assert "INFERX_API_KEY" in str(unset.value)

    # A name without a comma still means one credential, which is what it always meant.
    monkeypatch.setenv("TASK_SEARCH_KEY_ENV", "ALBERT_API_KEY,INFERX_API_KEY")
    assert cli._worker_credentials([]) == ["ALBERT_API_KEY", "INFERX_API_KEY"]


def test_a_run_records_which_build_of_the_harness_wrote_the_task(monkeypatch):
    """run.json pinned the plan, the prompt, the commit, the sandbox and hlink itself,
    and left `harness_version: null` -- the one program that actually writes the task was
    the only thing unrecorded. It drifts: a comment in this package still described
    OpenCode 1.18.20 while the machine had moved to 1.18.30."""
    from reasoning_core.task_search import implementation_runner as runner

    monkeypatch.setattr(runner.shutil, "which", lambda binary: f"/bin/{binary}")

    def fake_run(command, **kwargs):
        # mini prints its version and then exits 2 over the task it was not given, so a
        # non-zero status is not the same as having no version to report.
        answers = {"/bin/opencode": ("1.18.30\n", "", 0),
                   "/bin/mini": ("This is mini-swe-agent version 2.4.6.\nmore\n", "", 2),
                   "/bin/agy": ("", "1.2.2\n", 0)}
        out, err, code = answers[command[0]]
        return types.SimpleNamespace(stdout=out, stderr=err, returncode=code)

    monkeypatch.setattr(runner.subprocess, "run", fake_run)

    assert runner._harness_version("opencode") == "1.18.30"
    assert runner._harness_version("mini") == "2.4.6", "the version out of a sentence"
    assert runner._harness_version("agy") == "1.2.2", "read from stderr when that is where"

    # A harness that is not installed or will not answer leaves the field null rather than
    # failing the run: an unrecorded version is worth less than a wave.
    monkeypatch.setattr(runner.shutil, "which", lambda binary: None)
    assert runner._harness_version("opencode") is None


def _drafts(*ids):
    return [types.SimpleNamespace(trial_id=trial_id) for trial_id in ids]


def test_every_idea_s_first_draft_is_queued_before_any_second():
    from reasoning_core.task_search.implementation_runner import _siblings_last

    order = _siblings_last(_drafts("P001v1", "P001v2", "P001v3", "P002v1", "P002v2"))
    assert [trial.trial_id for trial in order] == [
        "P001v1", "P002v1", "P001v2", "P002v2", "P001v3"]


def _settling(verdict="VALID", fidelity="REALIZES", exhausted=False, status="success"):
    return {"status": status, "sample_sanity": {"verdict": verdict},
            "sample_fidelity": {"verdict": fidelity}, "steps": {"exhausted": exhausted}}


@pytest.mark.parametrize("result, settles", [
    (_settling(), True),
    (_settling(verdict=None), False),
    (_settling(fidelity="SUBSTITUTES"), False),
    (_settling(exhausted=True), False),
    (_settling(status="timed_out"), False),
])
def test_only_a_draft_no_sibling_could_outrank_settles_its_idea(result, settles):
    from reasoning_core.task_search.triage import settles as settles_idea

    assert settles_idea(result) is settles


def test_a_settled_idea_skips_the_drafts_that_have_not_started():
    from reasoning_core.task_search.implementation_runner import _skipping_settled

    plan = types.SimpleNamespace(name="w_r1", proposal_wave="w")
    outcomes = {"P001v1": _settling(), "P002v1": _settling(fidelity=None),
                "P002v2": _settling()}
    ran = []

    def run(_plan, trial):
        ran.append(trial.trial_id)
        return outcomes.get(trial.trial_id, _settling(status="timed_out"))

    run_one = _skipping_settled(plan, run)
    results = {trial.trial_id: run_one(plan, trial)
               for trial in _drafts("P001v1", "P002v1", "P001v2", "P002v2", "P001v3", "P002v3")}
    # P002v1 was unread by fidelity, so a sibling could still beat it and P002v2 ran.
    assert ran == ["P001v1", "P002v1", "P002v2"]
    assert results["P001v2"] == {"schema_version": 1, "wave": "w_r1", "proposal_wave": "w",
                                 "trial_id": "P001v2", "status": "superseded",
                                 "superseded_by": "P001v1"}
    assert results["P002v3"]["superseded_by"] == "P002v2"


def test_the_runs_root_is_a_machine_setting_with_the_checkout_as_fallback(tmp_path, monkeypatch):
    from reasoning_core.task_search.implementation_runner import RUNS_ROOT_VAR, default_runs_root

    repo = tmp_path / "reasoning_core"
    repo.mkdir()
    monkeypatch.delenv(RUNS_ROOT_VAR, raising=False)
    assert default_runs_root(repo) == tmp_path / ".reasoning_core-task-search"
    monkeypatch.setenv(RUNS_ROOT_VAR, str(tmp_path / "local"))
    assert default_runs_root(repo) == tmp_path / "local"
