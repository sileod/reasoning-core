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


def test_a_landing_pass_adds_what_it_landed_to_the_manifest(tmp_path, monkeypatch):
    """`_discover_tasks` rglobs the tasks tree, so the registered set is whatever is on
    disk and `tests/task_manifest.txt` is what makes it a deliberate list instead. Its
    test says the manifest is updated in the same commit as the task; leaving that to
    hand meant 184 landed tasks drifted out of it and the test was red for weeks, which
    is the same as not having the test at all."""
    from reasoning_core.task_search import land

    manifest = tmp_path / "task_manifest.txt"
    manifest.write_text("already_here\nzebra_task\n")
    monkeypatch.setattr(land, "MANIFEST", manifest)

    added = land.record_in_manifest(["new_task", "already_here"])

    assert added == ("new_task",), "only what was not already registered is reported"
    assert manifest.read_text().split() == ["already_here", "new_task", "zebra_task"], (
        "the manifest stays sorted, so a landing pass is a small readable diff")

    # Landing nothing new must not rewrite the file: a no-op pass that dirties the tree
    # is a pass someone has to review.
    before = manifest.stat().st_mtime_ns
    assert land.record_in_manifest(["new_task"]) == ()
    assert manifest.stat().st_mtime_ns == before
