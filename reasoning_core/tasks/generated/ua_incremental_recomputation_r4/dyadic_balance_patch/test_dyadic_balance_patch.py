import random

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.dyadic_balance_patch.dyadic_balance_patch import (
    DyadicBalancePatch,
    DyadicBalancePatchConfig,
    _min_splits,
)

SEED = 3867019559


def _make(level):
    random.seed(SEED + level)
    task = DyadicBalancePatch()
    task.config.set_level(level)
    return task


def test_gold_scores_one_across_levels():
    for level in range(7):
        random.seed(SEED + level)
        task = DyadicBalancePatch()
        task.config.set_level(level)
        seen = set()
        for _ in range(40):
            ex = task.generate_entry()
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
        assert len(seen) > 1, f"level {level} produced a single answer {seen}"


def test_junk_and_empty_score_zero():
    task = DyadicBalancePatch()
    ex = task.generate_entry()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0
    assert task.score_answer("-3", ex) == 0.0 or ex.answer == "-3"


def test_no_single_answer_dominates():
    task = DyadicBalancePatch()
    task.config.set_level(0)
    counts = {}
    random.seed(SEED)
    for _ in range(200):
        ex = task.generate_entry()
        counts[ex.answer] = counts.get(ex.answer, 0) + 1
    assert len(counts) >= 2, counts
    top = max(counts.values()) / 200.0
    assert top <= 0.75, counts


def test_min_splits_known_small():
    assert _min_splits([100, 100, 100, 100], 1) == 0
    assert _min_splits([100, 100, 100], 1) == 0
    assert _min_splits([1, 1, 1, 1], 3) == 1
    assert _min_splits([1, 1, 1, 1], 1) == 3


def test_metadata_json_serializable():
    import json

    task = DyadicBalancePatch()
    ex = task.generate_entry()
    json.dumps(ex.metadata)


def test_difficulty_changes_config():
    c = DyadicBalancePatchConfig()
    c.set_level(0)
    lo = c.L
    c2 = DyadicBalancePatchConfig()
    c2.set_level(6)
    assert c2.L > lo
