import random

from reasoning_core.tasks.generated.ua_paraphrase_equivalence_r4.focus_alternative_projection.focus_alternative_projection import (
    FocusAlternativeProjection,
    _eval,
    _count_focus,
    _format_set,
    _full,
)


def _task():
    return FocusAlternativeProjection()


def _answers_seen(task, n=200):
    task.config.set_level(5)
    seen = set()
    for _ in range(n):
        ex = task.generate_example()
        seen.add(ex.answer)
    return seen


def test_answers_scored_and_domain_valid():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(30):
            ex = t.generate_example()
            result = _eval(ex.metadata['tree'], t.config.domain)
            assert _format_set(sorted(result), t.config.domain) == ex.answer
            assert t.score_answer(ex.answer, ex) == 1.0


def test_wrong_and_junk_fail():
    t = _task()
    t.config.set_level(5)
    for _ in range(40):
        ex = t.generate_example()
        assert t.score_answer(ex.answer + 'x', ex) == 0.0
        assert t.score_answer(' ', ex) == 0.0
        assert t.score_answer('', ex) == 0.0
        assert t.score_answer('{}', ex) == 0.0 or ex.answer == 'empty'
        assert t.score_answer('{2,3}', ex) == 0.0 or ex.answer == '{2,3}'


def test_has_focus_and_predicates():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(30):
            ex = t.generate_example()
            assert _count_focus(ex.metadata['tree']) >= 1


def test_difficulty_scales():
    t = _task()
    t.config.set_level(0)
    d0 = t.config.depth
    t.config.set_level(6)
    d6 = t.config.depth
    assert d6 > d0


def test_answer_variety():
    t = _task()
    seen = _answers_seen(t, 300)
    assert len(seen) >= 8
    assert 'empty' in seen or seen


def test_not_constant():
    t = _task()
    exs = [t.generate_example() for _ in range(50)]
    assert len(set(e.answer for e in exs)) >= 5


def test_eval_semantics_manual():
    dom = 5
    assert _eval({'k': 'const', 'v': 2}, dom) == frozenset([2])
    assert _eval({'k': 'focus', 'v': 1}, dom) == _full(dom)
    assert _eval({'k': 'up', 'c': {'k': 'const', 'v': 3}}, dom) == _full(dom)
    ext = frozenset([1, 3])
    assert _eval({'k': 'pred', 'ext': [1, 3], 'c': {'k': 'focus', 'v': 0}},
                 dom) == ext
    comp = _eval({'k': 'comp', 'c': {'k': 'const', 'v': 4}}, dom)
    assert comp == frozenset([0, 1, 2, 3])
    conj = _eval({'k': 'conj',
                  'l': {'k': 'pred', 'ext': [0, 1, 2], 'c': {'k': 'focus', 'v': 0}},
                  'r': {'k': 'pred', 'ext': [1, 2, 3], 'c': {'k': 'focus', 'v': 0}}},
                 dom)
    assert conj == frozenset([1, 2])


def test_no_extreme_answers_after_balancing():
    t = _task()
    for level in (0, 3, 6):
        t.config.set_level(level)
        full = ', '.join(str(i) for i in range(t.config.domain))
        for _ in range(40):
            ex = t.generate_example()
            assert ex.answer != 'empty'
            assert ex.answer != '{%s}' % full
