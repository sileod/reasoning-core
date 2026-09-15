import random

from reasoning_core.tasks.generated.wave12.d_separation.d_separation import (
    d_separation,
)


def test_generate_and_score():
    task = d_separation()
    task.config.set_level(3)
    random.seed(42)
    seen = set()
    counts = {"yes": 0, "no": 0}
    for _ in range(60):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert entry.answer in ("yes", "no")
        counts[entry.answer] += 1
        seen.add(entry.answer)
    assert seen == {"yes", "no"}
    assert min(counts.values()) > 5


def test_score_rejects_junk():
    task = d_separation()
    task.config.set_level(0)
    random.seed(1)
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("garbage", entry) < 1.0
    assert task.score_answer(entry.answer.upper() + " ", entry) == 1.0


def test_all_levels():
    task = d_separation()
    for level in range(6):
        task.config.set_level(level)
        random.seed(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
