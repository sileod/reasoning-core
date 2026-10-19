from pathlib import Path

from reasoning_core.task_search.gepa_search import ORDER, score
from reasoning_core.task_search.implementor_prompt import render_implementor_prompt
from reasoning_core.task_search.plan import load_plan

ROOT = Path(__file__).parents[2]
PLAN = ROOT / "reasoning_core" / "task_search" / "plans" / "wave0.yaml"


def test_failures_score_by_how_far_down_the_gates_they_got():
    values = [score({"status": status})[0] for status in ORDER]
    assert values == sorted(values) and values[-1] < 0.4
    assert score({"status": "orchestration_error"})[0] == 0


def test_a_success_scores_above_every_failure_and_by_its_judges():
    def row(level, correct, glance):
        return {"level": level, "jev": {"correct": correct, "wellposed": 1.0,
                                        "shortcut": 0.0, "glance": glance}}

    good, parts = score({"status": "success"}, [row(0, 1.0, 0.9), row(6, 1.0, 0.1)],
                        ("other_task", 0.3, 0.7))
    bad, _ = score({"status": "success"}, [row(0, 0.2, 0.9), row(6, 0.2, 0.9)],
                   ("other_task", 0.95, 0.0))
    assert 1 >= good > bad >= 0.5 > 0.4
    assert parts["hard_at_top"] == 0.9 and parts["novel"] == 0.7
    assert score({"status": "success"})[0] == 0.5


def test_notes_are_appended_and_absent_notes_change_nothing():
    plan = load_plan(PLAN)
    trial = plan.trials[0]
    plain = render_implementor_prompt(plan, trial, ROOT)
    assert render_implementor_prompt(plan, trial, ROOT, notes=None) == plain
    noted = render_implementor_prompt(plan, trial, ROOT, notes="Bound every loop.")
    assert noted.startswith(plain) and noted.endswith("Bound every loop.\n")


def test_workers_get_only_the_chosen_providers_keys(capsys):
    from reasoning_core.task_search.implementation_runner import _provider_credentials
    names = ("ALBERT_API_KEY", "INFERX_API_KEY", "OPENROUTER_API_KEY")
    assert _provider_credentials(names, "albert", None) == ("ALBERT_API_KEY",)
    assert "OPENROUTER_API_KEY" in capsys.readouterr().err
    assert _provider_credentials(names, "albert", "orfree") == (
        "ALBERT_API_KEY", "OPENROUTER_API_KEY")
    import pytest
    with pytest.raises(ValueError):
        _provider_credentials(names, None, None)


def test_spend_cap_counts_step_costs_and_trips_only_past_the_budget(tmp_path, monkeypatch):
    import json
    from reasoning_core.task_search import spend
    events = tmp_path / "events.jsonl"
    events.write_text("".join(json.dumps(e) + "\n" for e in (
        {"type": "step_finish", "part": {"cost": 0.25}},
        {"type": "text", "part": {}},
        {"type": "step_finish", "part": {"cost": 0}},
    )) + '{"type": "step_fin')
    ledger = tmp_path / "spend.tsv"
    monkeypatch.delenv(spend.BUDGET_VAR, raising=False)
    assert spend.trial_cost(events) == 0.25
    assert not spend.over(0.0, ledger)          # free provider: never trips
    assert spend.over(spend.trial_cost(events), ledger)
    spend.record("w/T1", 0.0, ledger)
    assert not ledger.exists()
    spend.record("w/T1", 0.25, ledger)
    monkeypatch.setenv(spend.BUDGET_VAR, "1")
    assert spend.spent(ledger) == 0.25 and not spend.over(0.5, ledger)
    assert spend.over(0.8, ledger)


def test_an_opencode_2_rate_limit_is_retried(tmp_path):
    import json
    from reasoning_core.task_search.implementation_runner import _retryable_harness_failure
    log = tmp_path / "events.jsonl"
    log.write_text(json.dumps({"type": "error", "error": {
        "type": "provider.quota", "message": "Rate limit exceeded.", "status": 429}}) + "\n")
    result = {"status": "harness_failed", "harness_exit_code": 1, "harness_log": str(log)}
    assert _retryable_harness_failure(result) == "provider_429"
