from reasoning_core.tasks.generated.ua_systematic_generalization_r4.ordinal_limit_descent.ordinal_limit_descent import (
    OrdinalLimitDescent,
    _add,
    _cmp,
    _descent,
    _mono,
    _ord_str,
    _predecessor,
)


def _nat(k):
    return _mono((), k)


def test_predecessor_naturals():
    assert _predecessor(_nat(1)) == ()
    assert _predecessor(_nat(5)) == _nat(4)
    assert _predecessor(_mono(_mono((), 1), 1)) is None


def test_cmp():
    assert _cmp(_nat(1), _nat(2)) < 0
    assert _cmp(_nat(3), _nat(3)) == 0
    assert _cmp(_nat(2), _mono(_mono((), 1), 1)) < 0
    assert _cmp(_mono(_mono((), 1), 1), _nat(2)) > 0


def test_add_normalizes():
    assert _add(_nat(2), _nat(3)) == _nat(5)
    o = _add(_mono(_mono((), 1), 1), _nat(1))
    assert _ord_str(o) == "w^(1)+1"


def test_descent_successor_subtracts_one():
    o = _add(_mono(_mono((), 1), 1), _nat(5))
    r = _descent(o, 3)
    assert _cmp(r, o) < 0
    assert _ord_str(r) == "w^(1)+4"


def test_descent_w_to_n():
    assert _ord_str(_descent(_mono(_mono((), 1), 1), 3)) == "3"


def test_descent_decreases_for_all_levels():
    task = OrdinalLimitDescent()
    task.config.set_level(6)
    for _ in range(50):
        ex = task.generate_entry()
        assert ex is not None
        assert task.score_answer(ex.answer, ex) == 1.0


def test_scoring_roundtrip():
    task = OrdinalLimitDescent()
    for level in (0, 3, 6):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("0", ex) < 1.0
        assert task.score_answer(ex.metadata["alpha"], ex) < 1.0


def test_validate():
    task = OrdinalLimitDescent()
    task.validate(n_samples=4)
