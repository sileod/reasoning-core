from pathlib import Path

from reasoning_core.task_search.land import _record
from reasoning_core.task_search.plan import Trial


def _trial(design_choice):
    return Trial(trial_id="P001v1", idea="an idea", instruction="do it",
                 owned_path="reasoning_core/tasks/generated/w/t", validation=(),
                 design_choice=design_choice)


def test_landing_records_the_assignment_from_the_plan_not_the_worktree():
    """The implementor is asked to copy its assigned approach into the module, and mostly
    does -- but a missing attribute and a genuine baseline read identically, which is the
    one comparison the baseline variant exists to support. The plan knows for certain."""
    guided = _record("t", {"trial": "P001v1"}, _trial("Index by suffix array."),
                     Path("reasoning_core/tasks/generated/w/t"))
    baseline = _record("t", {"trial": "P001v3"}, _trial(""),
                       Path("reasoning_core/tasks/generated/w/t"))

    assert guided["design_choice"] == "Index by suffix array."
    assert guided["guided"] is True
    assert baseline["design_choice"] == ""
    assert baseline["guided"] is False, "an unguided baseline must be tellable from a task"
