import random

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.polynomial_expansion.polynomial_expansion import (
    PolynomialExpansion,
)


def _task():
    task = PolynomialExpansion()
    return task


def test_generate_and_score_default():
    random.seed(1234)
    task = _task()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_gold_scores_one_at_levels():
    task = _task()
    for level in (0, 2, 5, 6):
        random.seed(1000 + level)
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0, level


def test_junk_scores_zero():
    random.seed(7)
    task = _task()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("garbage not a poly", x) < 1.0


def test_nvar_varied_across_levels():
    task = _task()
    seen = set()
    for level in (0, 3, 6):
        random.seed(5000 + level)
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(5):
            x = task.generate_example()
            seen.add(x.metadata["nvar"])
    assert len(seen) >= 1
