import random
from datetime import date, timedelta

from reasoning_core.tasks.generated.wave12.calendar_recurrence_execution.calendar_recurrence_execution import (
    CalendarRecurrenceExecution,
    CalendarRecurrenceConfig,
)


def test_gold_scores_one():
    task = CalendarRecurrenceExecution()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_scores_zero():
    task = CalendarRecurrenceExecution()
    ex = task.generate_example()
    assert task.score_answer("1999-01-01", ex) == 0.0
    assert task.score_answer("", ex) == 0.0


def test_difficulty_changes():
    cfg = CalendarRecurrenceConfig()
    cfg.set_level(0)
    l0 = (cfg.n, cfg.span_days)
    cfg.set_level(5)
    l5 = (cfg.n, cfg.span_days)
    assert l0 != l5


def test_occurrence_is_valid():
    task = CalendarRecurrenceExecution()
    ex = task.generate_example()
    d = date.fromisoformat(ex.answer)
    start = date.fromisoformat(ex.metadata["start"])
    end = date.fromisoformat(ex.metadata["end"])
    assert start <= d <= end
    days = [{"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}[x] for x in ex.metadata["days"]]
    assert d.weekday() in days


def test_metadata_json_serializable():
    import json

    task = CalendarRecurrenceExecution()
    ex = task.generate_example()
    json.dumps(ex.metadata)


def test_nth_counted_correctly():
    task = CalendarRecurrenceExecution()
    for _ in range(20):
        ex = task.generate_example()
        d = date.fromisoformat(ex.answer)
        start = date.fromisoformat(ex.metadata["start"])
        n = ex.metadata["n"]
        days = [{"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}[x] for x in ex.metadata["days"]]
        exc = []
        if ex.metadata["exclusions"]:
            for part in ex.metadata["exclusions"].split("; "):
                a, b = part.split(" to ")
                exc.append((date.fromisoformat(a), date.fromisoformat(b)))
        adj = set()
        if ex.metadata["adjustments"]:
            for part in ex.metadata["adjustments"].split("; "):
                adj.add(date.fromisoformat(part))
        count = 0
        cur = start
        while True:
            valid = cur.weekday() in days
            if valid and any(a <= cur <= b for a, b in exc):
                valid = False
            if valid and cur in adj:
                valid = False
            if valid:
                count += 1
                if count == n:
                    assert cur == d, (cur, d, ex.metadata)
                    break
            cur += timedelta(days=1)
