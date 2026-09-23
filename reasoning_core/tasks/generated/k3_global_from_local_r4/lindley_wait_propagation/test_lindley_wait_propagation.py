import random

from reasoning_core.tasks.generated.k3_global_from_local_r4.lindley_wait_propagation.lindley_wait_propagation import (
    LindleyWaitPropagation,
    waits,
)


def test_gold_scores_one():
    random.seed(1234)
    task = LindleyWaitPropagation()
    for _ in range(50):
        task.config.set_level(random.randrange(7))
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_and_empty_score_zero():
    random.seed(5)
    task = LindleyWaitPropagation()
    for _ in range(50):
        self0 = task.generate_example()
        assert task.score_answer("", self0) == 0.0
        assert task.score_answer("junk", self0) == 0.0


def test_waits_recursion_matches_direct_reference():
    a = [3, 2, 5, 1]
    s = [2, 4, 1, 3]
    w = waits(a, s)
    expected = []
    cur = 0
    for ai, si in zip(a, s):
        cur = max(0, cur - ai + si)
        expected.append(cur)
    assert w == expected
    assert all(x >= 0 for x in w)


def test_level_changes_config():
    task = LindleyWaitPropagation()
    task.config.set_level(0)
    c0 = task.config.count
    task.config.set_level(6)
    assert task.config.count > c0


def test_answers_within_domain():
    random.seed(777)
    task = LindleyWaitPropagation()
    for _ in range(100):
        task.config.set_level(random.randrange(7))
        e = task.generate_example()
        w = waits(e.metadata["arrivals"], e.metadata["services"])
        assert w[e.metadata["index"]] >= 0
        assert task.score_answer(str(w[e.metadata["index"]]), e) == 1.0
