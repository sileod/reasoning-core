"""The audit that makes a night's numbers recomputable instead of anecdotal."""
import json

import yaml

from reasoning_core.task_search.funnel import arm_report, wave_yield


def _archive(repo_root, name, wave):
    directory = repo_root / "reasoning_core" / "task_search" / "proposals" / "archive"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.yaml").write_text(yaml.safe_dump(wave, sort_keys=False))


def _plan(repo_root, name, trials):
    directory = repo_root / "reasoning_core" / "task_search" / "plans"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{name}.yaml").write_text(yaml.safe_dump(
        {"name": name, "trials": trials}, sort_keys=False))


def _trial(runs_root, plan, trial, status):
    directory = runs_root / plan / "20260915T000000Z" / trial
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "events.jsonl").write_text("")
    (directory / "run.json").write_text(json.dumps({"status": status}))


def _landed(repo_root, plan, task, trial):
    directory = repo_root / "reasoning_core" / "tasks" / "generated" / plan / task
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"generate_samples_{trial}.py").write_text("")


def test_a_short_critic_panel_is_counted_separately_from_a_split_one(tmp_path):
    """A two-sample panel turns the majority rule into unanimity, so `1/2` is refused
    where `2/3` would have passed. Both numbers are needed: `k3_relevance-separation` ran
    almost every rejection short and still accepted five, because few of them tied. It is
    the tie that costs a candidate, not the thin panel."""
    _archive(tmp_path, "brief", {
        "proposals": [{"name": "kept"}],
        "rejected": [
            {"name": "a", "reason": "1/2 samples judged it novel; known"},
            {"name": "b", "reason": "0/2 samples judged it novel; duplicate"},
            {"name": "c", "reason": "1/3 samples judged it novel; duplicate"},
            {"name": "d", "reason": "duplicate of existing plan"},
        ],
        "pool": [{"name": "unreached"}]})

    row, = wave_yield(tmp_path)

    assert (row["accepted"], row["rejected"], row["pooled"]) == (1, 4, 1)
    assert row["seen"] == 6, "the pool is part of what the wave paid for"
    assert row["tallied"] == 3, "a rejection with no tally cannot be scored for panel size"
    assert row["short_panel"] == 2
    assert row["split_panel"] == 1, "only the 1/2 was a tie; 0/2 was a verdict"


def test_the_baseline_is_measured_only_where_a_baseline_actually_ran(tmp_path):
    """The arm label is not the thing being measured. `wave9` calls its queues `v1`,
    `pilot` and `retry`, and `wave12` runs three guided arms, so counting every landed
    `...v1.py` as a win for guidance put it at 194 against 21 and 5 -- which says only how
    long `v1` has existed. Only a plan that left one trial unguided answers the question."""
    _plan(tmp_path, "compared", [
        {"id": "P001v1", "design_choice": "use a chase"},
        {"id": "P001v2", "design_choice": "use a tableau"},
        {"id": "P001v3", "design_choice": None},
    ])
    _plan(tmp_path, "all_guided", [
        {"id": "P001v1", "design_choice": "one"},
        {"id": "P001v2", "design_choice": "two"},
    ])
    runs = tmp_path.parent / f".{tmp_path.name}-task-search"
    for plan in ("compared", "all_guided"):
        for trial in ("P001v1", "P001v2", "P001v3"):
            _trial(runs, plan, trial, "success")
    _landed(tmp_path, "compared", "kept", "P001v3")
    _landed(tmp_path, "all_guided", "other", "P001v1")

    rows = {row["arm"]: row for row in arm_report(tmp_path, runs)}

    assert set(rows) == {"v1", "v2", "v3"}
    assert all(row["trials"] == 1 for row in rows.values()), (
        "a plan with no unguided trial is not an arm comparison")
    assert rows["v3"]["guided"] is False and rows["v3"]["landed"] == 1
    assert rows["v1"]["guided"] is True and rows["v1"]["landed"] == 0, (
        "a landing from an all-guided plan was credited to the baseline comparison")


def test_a_retried_attempt_is_not_a_second_trial(tmp_path):
    """A transient failure renames the corpse to `<trial>.attempt<N>-<reason>` and starts
    over. Overnight that left 28 of them, and counting them read as a wave twice the size
    with a harness failure rate to match."""
    _plan(tmp_path, "compared", [
        {"id": "P001v1", "design_choice": "guided"},
        {"id": "P001v2", "design_choice": None},
    ])
    runs = tmp_path.parent / f".{tmp_path.name}-task-search"
    _trial(runs, "compared", "P001v1", "success")
    _trial(runs, "compared", "P001v1.attempt1-provider_429", "harness_failed")
    _trial(runs, "compared", "P001v2", "success")

    rows = {row["arm"]: row for row in arm_report(tmp_path, runs)}

    assert rows["v1"]["trials"] == 1 and not rows["v1"]["failures"]
