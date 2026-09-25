import random

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.fermionic_normal_ordering.fermionic_normal_ordering import (
    FermionicNormalOrdering,
    _canonical_from_metadata,
    _normalize_expr,
    _verified,
)


def test_gold_scores_one():
    random.seed(1)
    task = FermionicNormalOrdering()
    for _ in range(20):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_metadata_roundtrip():
    random.seed(2)
    task = FermionicNormalOrdering()
    for _ in range(20):
        x = task.generate_example()
        gold = _canonical_from_metadata(x.metadata["canonical"])
        assert gold


def test_verified_holds():
    random.seed(3)
    task = FermionicNormalOrdering()
    for _ in range(20):
        x = task.generate_example()
        monomials = [[tuple(op) for op in mono] for mono in x.metadata["monomials"]]
        canonical = _canonical_from_metadata(x.metadata["canonical"])
        assert _verified(monomials, canonical)
        assert canonical == _normalize_expr(monomials)


def test_junk_scores_zero():
    random.seed(4)
    task = FermionicNormalOrdering()
    x = task.generate_example()
    for bad in ("", " ", "reajrjrje9595!", "1 + c0a0"):
        assert task.score_answer(bad, x) < 1.0


def test_levels_vary():
    random.seed(5)
    task = FermionicNormalOrdering()
    answers = set()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(15):
            answers.add(task.generate_example().answer)
    assert len(answers) >= 10


def test_level6_generates():
    random.seed(6)
    task = FermionicNormalOrdering()
    task.config.set_level(6)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0
