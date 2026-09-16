import random

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.hereditary_base_rewrite.hereditary_base_rewrite import (
    HereditaryBaseRewrite,
    _hereditary_repr,
    _parse_hereditary,
)

random.seed(12345)


def _task(level):
    t = HereditaryBaseRewrite()
    t.config.set_level(level)
    return t


def test_generate_and_score_all_levels():
    for level in range(7):
        t = _task(level)
        for _ in range(20):
            x = t.generate_example(level=level)
            assert t.score_answer(x.answer, x) == 1.0


def test_round_trip_hereditary():
    for base in (2, 3, 4, 5):
        for n in range(0, 1000):
            s = _hereditary_repr(n, base)
            assert _parse_hereditary(s, base) == n, (n, base, s)


def test_junk_scores_zero():
    t = _task(0)
    x = t.generate_example(level=0)
    assert t.score_answer("", x) == 0.0
    assert t.score_answer("not an answer", x) == 0.0


def test_difficulty_changes():
    t = _task(0)
    a = _task(0).config.max_start
    b = _task(6).config.max_start
    assert b > a
