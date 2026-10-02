"""The set of registered tasks is a deliberate choice, not whatever is on disk.

`_discover_tasks` rglobs the tasks tree, so an untracked scratch directory joins
DATASETS -- and therefore any fresh pool build -- in silence. That happened once
(18 probe tasks). When this test fails, either the drift is unintended or the
manifest needs updating in the same commit as the task.
"""
import pathlib

import reasoning_core

MANIFEST = pathlib.Path(__file__).parent / "task_manifest.txt"


def test_registered_tasks_match_manifest():
    expected = set(MANIFEST.read_text().split())
    actual = set(reasoning_core.DATASETS)
    assert actual == expected, (
        f"unexpected tasks: {sorted(actual - expected)}; "
        f"missing tasks: {sorted(expected - actual)}")


def test_every_roster_task_has_one_area():
    from reasoning_core.registry import AREAS
    listed = [task for tasks in AREAS.values() for task in tasks]
    assert len(listed) == len(set(listed)), "a task is listed in two areas"
    roster = set(reasoning_core.list_tasks())
    assert set(listed) == roster, (
        f"no area: {sorted(roster - set(listed))}; not in the roster: {sorted(set(listed) - roster)}")
