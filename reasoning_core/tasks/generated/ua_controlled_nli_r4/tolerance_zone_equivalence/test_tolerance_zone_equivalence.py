import random

from reasoning_core.tasks.generated.ua_controlled_nli_r4.tolerance_zone_equivalence.tolerance_zone_equivalence import (
    ToleranceZoneEquivalence,
    _point_in_rect,
)


def _independently_score(task, entry):
    shapes = entry.metadata["shapes"]
    t1 = entry.metadata["tol1"]
    t2 = entry.metadata["tol2"]
    acc1 = [i for i, v in enumerate(shapes) if any(_point_in_rect(p, t1) for p in v)]
    acc2 = [i for i, v in enumerate(shapes) if any(_point_in_rect(p, t2) for p in v)]
    return "equal" if acc1 == acc2 else "not_equal"


def test_gold_roundtrip():
    task = ToleranceZoneEquivalence()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_independent_verifier_matches():
    task = ToleranceZoneEquivalence()
    for _ in range(50):
        entry = task.generate_example()
        assert _independently_score(task, entry) == entry.metadata["answer"]


def test_both_labels_appear():
    task = ToleranceZoneEquivalence()
    seen = set()
    for _ in range(60):
        entry = task.generate_example()
        seen.add(entry.metadata["answer"])
    assert seen == {"equal", "not_equal"}


def test_difficulty_changes_config():
    task = ToleranceZoneEquivalence()
    task.config.set_level(0)
    base = (task.config.n_candidates, task.config.grid)
    task.config.set_level(6)
    high = (task.config.n_candidates, task.config.grid)
    assert high != base


def test_junk_and_empty_do_not_score():
    task = ToleranceZoneEquivalence()
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("something_random", entry) < 1.0
    assert task.score_answer(None, entry) < 1.0


def test_all_levels_generate():
    task = ToleranceZoneEquivalence()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        entry = task.generate_example()
        assert entry.metadata["answer"] in ("equal", "not_equal")
        assert task.score_answer(entry.answer, entry) == 1.0


def test_reproducible_seeded():
    random.seed(12345)
    task = ToleranceZoneEquivalence()
    e1 = task.generate_example()
    random.seed(12345)
    task2 = ToleranceZoneEquivalence()
    e2 = task2.generate_example()
    assert e1.answer == e2.answer
    assert e1.metadata["shapes"] == e2.metadata["shapes"]
