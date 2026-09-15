import reasoning_core.tasks.generated.k3_systematic_generalization_r1.regular_expression_derivative.regular_expression_derivative as mod
from reasoning_core.template import Task
from reasoning_core.tasks.generated.k3_systematic_generalization_r1.regular_expression_derivative.regular_expression_derivative import (
    _deriv, _gen, _matches, _nullable, _render, _simplify, _verify, _all_words,
)

ALPHABET = ('a', 'b')


def test_primitives():
    assert _matches(EPS := mod.EPS, '') is True
    assert _matches(mod.EPS, 'a') is False
    assert _matches('a', 'a') is True
    assert _matches('a', '') is False
    assert _matches(mod.EMPTY, '') is False
    assert _matches(('cat', 'a', 'b'), 'ab') is True
    assert _matches(('star', 'a'), '') is True
    assert _matches(('star', 'a'), 'aaa') is True
    assert _matches(('union', 'a', 'b'), 'b') is True


def test_simplify_identities():
    assert _simplify(('union', 'a', mod.EMPTY)) == 'a'
    assert _simplify(('union', mod.EMPTY, 'a')) == 'a'
    assert _simplify(('cat', 'a', mod.EMPTY)) == mod.EMPTY
    assert _simplify(('cat', mod.EPS, 'a')) == 'a'
    assert _simplify(('cat', 'a', mod.EPS)) == 'a'
    assert _simplify(('star', mod.EMPTY)) == mod.EPS
    assert _simplify(('star', mod.EPS)) == mod.EPS
    assert _simplify(('union', 'a', 'a')) == 'a'


def test_nullable():
    assert _nullable(mod.EPS) is True
    assert _nullable(mod.EMPTY) is False
    assert _nullable('a') is False
    assert _nullable(('star', 'a')) is True
    assert _nullable(('cat', mod.EPS, 'a')) is False
    assert _nullable(('cat', 'a', 'b')) is False


def test_verify_rules():
    for _ in range(300):
        expr = _simplify(_gen(4))
        if expr == mod.EMPTY or expr == mod.EPS:
            continue
        for ch in ALPHABET:
            d = _simplify(_deriv(ch, expr))
            assert _verify(ch, expr, d), (ch, _render(expr), _render(d))


def test_derivative_laws():
    assert _render(_deriv('a', 'a')) == '1'
    assert _render(_deriv('b', 'a')) == '0'
    assert _deriv('a', ('star', 'a')) == ('star', 'a')
    assert _verify('a', ('star', 'a'), _deriv('a', ('star', 'a')))


def test_contract_roundtrip():
    t = mod.RegExpDerivative()
    for level in (0, 6):
        t.config.set_level(level)
        for _ in range(20):
            x = t.generate_example()
            assert x.answer is not None
            assert t.score_answer(x.answer, x) == 1.0
            assert t.score_answer('', x) < 1.0
            assert t.score_answer('zzz', x) < 1.0


def test_answers_varied():
    t = mod.RegExpDerivative()
    t.config.set_level(0)
    answers = {t.generate_example().answer for _ in range(200)}
    assert len(answers) > 5


def test_every_level_generates():
    t = mod.RegExpDerivative()
    for level in range(7):
        t.config.set_level(level)
        answers = [t.generate_example().answer for _ in range(30)]
        assert len(set(answers)) >= 5, level


def test_metadata_json_serializable():
    import json
    t = mod.RegExpDerivative()
    t.config.set_level(3)
    for _ in range(10):
        ex = t.generate_example()
        json.dumps(ex.metadata)


def test_no_single_answer_dominates():
    from collections import Counter
    t = mod.RegExpDerivative()
    for level in (0, 3, 6):
        t.config.set_level(level)
        c = Counter(t.generate_example().answer for _ in range(200))
        top = max(c.values()) / sum(c.values())
        assert top <= 0.55, (level, c.most_common(3))
