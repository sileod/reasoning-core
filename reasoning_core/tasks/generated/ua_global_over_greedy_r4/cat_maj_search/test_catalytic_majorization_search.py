from fractions import Fraction
import json
import random

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.catalytic_majorization_search. \
    catalytic_majorization_search import (
    CatMajSearch, _majorized_by, _min_dim, _compositions,
)


def test_roundtrip():
    task = CatMajSearch()
    for level in (0, 2, 5):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1
        assert task.render_prompt(ex.metadata)
        json.dumps(dict(ex.metadata))


def test_answer_domain():
    task = CatMajSearch()
    for level in (0, 2, 5):
        for _ in range(30):
            ex = task.generate_example(level=level)
            a = ex.answer
            D = ex.metadata['D']
            assert a == 'none' or (a.isdigit() and 1 <= int(a) <= D)


def test_garbage_scores_zero():
    task = CatMajSearch()
    ex = task.generate_example()
    assert task.score_answer('', ex) < 1
    assert task.score_answer('xyz', ex) < 1


def test_w_precedes_x_gives_dim1():
    w = [Fraction(1, 2), Fraction(1, 2)]
    x = [Fraction(1, 3), Fraction(2, 3)]
    D = 8
    assert _majorized_by(w, x)
    assert _min_dim(w, x, D, None) == 1


def test_fixed_last_respected():
    w = [Fraction(1, 2), Fraction(1, 2)]
    x = [Fraction(1, 3), Fraction(2, 3)]
    D = 4
    d = _min_dim(w, x, D, 4)
    assert d == 1 or d is None
    d2 = _min_dim(w, x, D, 3)
    assert d2 is None or (1 <= d2 <= 3)


def test_fixed_last_last_part():
    w = [Fraction(1, 4), Fraction(3, 4)]
    x = [Fraction(2, 4), Fraction(2, 4)]
    D = 5
    d = _min_dim(w, x, D, 2)
    assert d is None or (1 <= d <= 5)


def test_compositions():
    assert sorted(sum(parts) for parts in _compositions(4)) == [4] * 8
    assert len(list(_compositions(4))) == 8


def test_difficulty_changes_config():
    task = CatMajSearch()
    c0 = task.config.to_dict()
    task.config.set_level(3)
    assert task.config != c0


def test_deterministic():
    random.seed(123)
    a = CatMajSearch().generate_example(level=2)
    random.seed(123)
    b = CatMajSearch().generate_example(level=2)
    assert a.prompt == b.prompt and a.answer == b.answer
