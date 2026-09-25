import random

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.independence_axiom_entailment.independence_axiom_entailment import (
    IndependenceAxiomEntailment,
    IndependenceConfig,
    _axiom_closure,
    _canon,
)


def _setup(seed=1):
    random.seed(seed)
    cfg = IndependenceConfig()
    task = IndependenceAxiomEntailment(cfg)
    return task


def test_gold_scores_one():
    random.seed(42)
    task = IndependenceAxiomEntailment()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_garbage():
    random.seed(7)
    task = IndependenceAxiomEntailment()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("banana", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0
    assert task.score_answer(123, ex) == 0.0


def test_wrong_answer_zero():
    random.seed(9)
    task = IndependenceAxiomEntailment()
    for _ in range(20):
        ex = task.generate_example()
        other = "no" if ex.answer == "yes" else "yes"
        assert task.score_answer(other, ex) == 0.0


def test_closure_symmetry():
    a, b, c = frozenset({1}), frozenset({2}), frozenset({3, 4})
    clos = _axiom_closure([(a, b, c)], frozenset({1, 2, 3, 4}), False)
    assert _canon(b, a, c) in clos


def test_balance_across_levels():
    for lvl in (0, 2, 5):
        random.seed(100 + lvl)
        cfg = IndependenceConfig()
        cfg.set_level(lvl)
        task = IndependenceAxiomEntailment(cfg)
        yes = 0
        total = 40
        for _ in range(total):
            ex = task.generate_example()
            if ex.answer == "yes":
                yes += 1
        assert 0.2 * total <= yes <= 0.8 * total, (lvl, yes, total)


def test_difficulty_changes_config():
    cfg = IndependenceConfig()
    cfg.set_level(0)
    n0 = (cfg.n_vars, cfg.n_premises)
    cfg.set_level(6)
    n6 = (cfg.n_vars, cfg.n_premises)
    assert n0 != n6
    assert n6[0] > n0[0]
