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
