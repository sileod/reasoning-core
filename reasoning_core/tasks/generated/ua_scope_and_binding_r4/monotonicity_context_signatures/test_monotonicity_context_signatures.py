import random

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.monotonicity_context_signatures.monotonicity_context_signatures import (
    MonotonicityContextSignatures,
    _build,
    _compose,
    _context_above,
)


def _task():
    return MonotonicityContextSignatures()


def test_answers_are_valid_and_scored():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(30):
            ex = t.generate_example()
            assert ex.answer in ('+', '-', '0')
            assert t.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_fail():
    t = _task()
    t.config.set_level(5)
    for _ in range(30):
        ex = t.generate_example()
        for o in ('+', '-', '0'):
            if o != ex.answer:
                assert t.score_answer(o, ex) != 1.0


def test_extreme_junk():
    t = _task()
    ex = t.generate_example()
    for junk in ('', '  ', 'plus', '++', ','):
        assert t.score_answer(junk, ex) == 0.0


def test_semantics_compose():
    assert _compose('+', '+') == '+'
    assert _compose('-', '-') == '+'
    assert _compose('+', '-') == '-'
    assert _compose('-', '+') == '-'
    assert _compose('+', '0') == '0'
    assert _compose('0', '+') == '0'


def test_difficulty_scales():
    t = _task()
    t.config.set_level(0)
    l0 = t.config.leaves
    t.config.set_level(6)
    l6 = t.config.leaves
    assert l6 > l0


def test_label_balance_smoke():
    t = _task()
    t.config.set_level(4)
    counts = {'+': 0, '-': 0, '0': 0}
    for _ in range(400):
        ex = t.generate_example()
        counts[ex.answer] += 1
    assert counts['0'] < 240
    assert counts['0'] > 40


def test_context_matches_manual():
    tree = [
        {'id': 0, 'pol': '+', 'op': 'NONE', 'lex': None},
        {'id': 1, 'pol': '+', 'op': 'NEG', 'lex': None},
    ]
    assert _context_above(tree, 0) == '-'
    ctx = _compose('+', _context_above(tree, 0))
    assert ctx == '-'
