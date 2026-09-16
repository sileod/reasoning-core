import random

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.scalar_alternative_exclusion.scalar_alternative_exclusion import (
    ScalarAlternativeExclusion,
    _parse_set,
)


def _make(level=0):
    random.seed(7)
    return ScalarAlternativeExclusion(config=ScalarAlternativeExclusion.config_cls()).generate_example(level=level)


def test_gold_scores_one():
    task = ScalarAlternativeExclusion()
    for level in (0, 2, 5):
        for _ in range(20):
            entry = task.generate_example(level=level)
            assert task.score_answer(entry.answer, entry) == 1.0
            assert entry.answer == ",".join(str(i) for i in entry.metadata["surviving"])


def test_garbage_scores_zero():
    task = ScalarAlternativeExclusion()
    entry = task.generate_example()
    for bad in ("", " ", "reajrjrje9595!", "1,2,9", "0", "nine"):
        assert task.score_answer(bad, entry) == 0.0


def test_answer_is_ascending_set():
    task = ScalarAlternativeExclusion()
    for _ in range(50):
        entry = task.generate_example()
        parsed = _parse_set(entry.answer)
        surviving = [int(x) for x in entry.answer.split(",")]
        assert parsed == frozenset(surviving)
        assert sorted(surviving) == surviving and len(set(surviving)) == len(surviving)
