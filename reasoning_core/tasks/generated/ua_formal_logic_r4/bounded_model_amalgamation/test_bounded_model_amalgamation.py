import random

from reasoning_core.tasks.generated.ua_formal_logic_r4.bounded_model_amalgamation.bounded_model_amalgamation import (
    BoundedModelAmalgamation,
    _min_analysis,
)


def _gold(k, generators, clauses):
    best, bc = _min_analysis(k, [tuple(g) for g in generators], [tuple(c) for c in clauses])
    if best is None:
        return "none"
    return f"({best},{bc})"


def test_gold_scores_one():
    random.seed(1)
    t = BoundedModelAmalgamation()
    t.config.set_level(0)
    for _ in range(20):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_manual_instance():
    # 2 variables, G0 forces x0 true, constraint not(x0 and x1) -> x0 true, x1 false => size1, 1 witness
    best, bc = _min_analysis(2, [(1, 0)], [(0, 1)])
    assert (best, bc) == (1, 1)


def test_wrong_answers_rejected():
    random.seed(2)
    t = BoundedModelAmalgamation()
    t.config.set_level(2)
    e = t.generate_example()
    assert t.score_answer("", e) < 1.0
    assert t.score_answer("junk", e) < 1.0
    assert t.score_answer("(0,0)", e) < 1.0


def test_answer_domain():
    random.seed(3)
    t = BoundedModelAmalgamation()
    for lvl in range(7):
        t.config.set_level(lvl)
        e = t.generate_example()
        best, bc = _min_analysis(e.metadata["k"], [tuple(g) for g in e.metadata["generators"]],
                                 [tuple(c) for c in e.metadata["clauses"]])
        assert best is not None
        assert 0 <= best <= e.metadata["k"]
        assert 1 <= bc <= 9
        assert e.answer == f"({best},{bc})"


def test_levels_change():
    t = BoundedModelAmalgamation()
    t.config.set_level(0)
    k0 = t.config.k
    t.config.set_level(6)
    k6 = t.config.k
    assert k6 > k0
