import random

import pytest

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.exact_relabeling_tail_count.exact_relabeling_tail_count import (
    ExactRelabelingTailCount,
    _group_size,
    _tail_count,
)

TASK = ExactRelabelingTailCount()


def test_group_size_monotonic():
    sizes = [_group_size(i) for i in range(7)]
    assert sizes == [2, 3, 3, 4, 4, 5, 5]


def test_each_level_generates_and_scores():
    random.seed(11)
    for level in range(7):
        TASK.config.set_level(level)
        ex = TASK.generate_example()
        assert TASK.score_answer(ex.answer, ex) == 1.0


def test_answer_is_balanced_range():
    random.seed(22)
    seen = set()
    for _ in range(60):
        TASK.config.set_level(3)
        ex = TASK.generate_example()
        seen.add(ex.answer)
        assert 1 <= int(ex.answer) <= ex.metadata["n_subsets"]
    assert len(seen) > 1


def test_tail_count_includes_observed():
    random.seed(33)
    TASK.config.set_level(1)
    ex = TASK.generate_example()
    assert int(ex.answer) >= 1


def test_all_combos_recomputed():
    random.seed(44)
    for k in (2, 3, 5):
        n = 2 * k
        total = 0
        for combo in __import__("itertools").combinations(range(n), k):
            s = sum(combo) + k
            total += _tail_count(n, k, s)
        n_subsets = 1
        for i in range(1, k + 1):
            n_subsets = n_subsets * (n - k + i) // i
        assert total >= n_subsets


def test_junk_and_empty_score_zero():
    random.seed(55)
    TASK.config.set_level(2)
    ex = TASK.generate_example()
    assert TASK.score_answer("", ex) == 0.0
    assert TASK.score_answer("not-a-number", ex) == 0.0
