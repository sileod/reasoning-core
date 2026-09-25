import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.interval_matrix_regularity.interval_matrix_regularity import (
    IntervalMatrixConfig,
    IntervalMatrixRegularity,
    _first_singular_radius,
    _gen_regular,
    _gen_singular,
    _det,
)


def test_config_difficulty():
    cfg = IntervalMatrixConfig()
    cfg.set_level(6)
    assert cfg.n == 3
    assert cfg.max_radius >= 4
    cfg.set_level(0)
    assert cfg.n == 2


def test_generate_entry_shapes():
    t = IntervalMatrixRegularity()
    for level in (0, 2, 5, 6):
        ex = t.generate_example(level=level)
        assert isinstance(ex, Entry)
        assert ex.metadata['n'] in (2, 3)
        assert isinstance(ex.answer, str)
        assert t.score_answer(ex.answer, ex) == 1.0


def test_answer_formats():
    t = IntervalMatrixRegularity()
    for _ in range(100):
        ex = t.generate_example(level=random.randint(0, 6))
        a = ex.answer
        if a != 'regular':
            assert a.startswith('singular_at_')
            r = int(a.split('_')[-1])
            assert 0 <= r <= ex.metadata['radius']


def test_score_garbage():
    t = IntervalMatrixRegularity()
    ex = t.generate_example(level=2)
    assert t.score_answer('regular', ex) in (0.0, 1.0)
    assert t.score_answer('', ex) == 0.0
    assert t.score_answer('junk', ex) == 0.0


def test_regular_branch_is_regular():
    random.seed(1)
    for _ in range(50):
        matrix, groups = _gen_regular(2, 3)
        assert _first_singular_radius(matrix, groups, 3) is None


def test_singular_branch_reaches_exact_radius():
    random.seed(2)
    for _ in range(50):
        matrix, groups = _gen_singular(2, 4)
        r = _first_singular_radius(matrix, groups, 4)
        assert r is not None and 1 <= r <= 4


def test_determinant_helper():
    assert _det([[1, 2], [3, 4]]) == -2
    assert _det([[1, 2, 3], [4, 5, 6], [7, 8, 10]]) == -3
