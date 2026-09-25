import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.discrete_tomographic_completion.task import (
    DiscreteTomographicCompletion,
    score_answer,
)


def test_roundtrip():
    task = DiscreteTomographicCompletion()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(30):
            x = task.generate_example()
            assert x.answer is not None
            assert score_answer(x.answer, x) == 1.0
            assert 0.0 <= score_answer("", x) < 1.0
            assert 0.0 <= score_answer("junk", x) < 1.0
    assert len(task.summary) > 0


def test_answer_types_balance():
    task = DiscreteTomographicCompletion()
    task.config.set_level(3)
    seen = set()
    for _ in range(200):
        x = task.generate_example()
        seen.add(x.metadata["answer_type"])
    assert seen == {"forced", "range", "unique"}


def test_domain_validity():
    task = DiscreteTomographicCompletion()
    task.config.set_level(6)
    for _ in range(40):
        x = task.generate_example()
        if x.metadata["answer_type"] == "range":
            lo, hi = map(int, x.answer.split())
            assert 0 <= lo <= 1 and 0 <= hi <= 1 and lo <= hi
        else:
            assert int(x.answer) in (0, 1)
