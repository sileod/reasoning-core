import random

from reasoning_core.tasks.generated.ua_counterfactual_r4.stratified_reversal_intervention.stratified_reversal_intervention import (
    StratifiedReversalIntervention, _apply, _valid, _pooled, _parse_answer,
    _format_ops, IMPOSSIBLE,
)


def test_gold_scores_one_at_all_levels():
    task = StratifiedReversalIntervention()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_impossible_validated():
    task = StratifiedReversalIntervention()
    task.config.set_level(1)
    for _ in range(30):
        ex = task.generate_example()
        if ex.answer == IMPOSSIBLE:
            data = ex.metadata
            pooled = data["pooled"]
            threshold = data["threshold"]
            assert "ops" in data
            assert data["ops"] is None
            # flipping would require more than max_ops
            need = abs(threshold - pooled)
            assert need >= 1


def test_solvable_gold_really_flips_and_stays_valid():
    task = StratifiedReversalIntervention()
    task.config.set_level(1)
    seen = 0
    for _ in range(40):
        ex = task.generate_example()
        if ex.answer == IMPOSSIBLE:
            continue
        seen += 1
        data = ex.metadata
        tables = data["tables"]
        threshold = data["threshold"]
        ops = _parse_answer(ex.answer, ex)
        assert ops is not None
        newt = _apply(tables, ops)
        assert _valid(newt, tables)
        before = _pooled(tables) >= threshold
        after = _pooled(newt) >= threshold
        assert before != after
    assert seen > 0


def test_metadata_json_serializable():
    import json
    task = StratifiedReversalIntervention()
    task.config.set_level(4)
    ex = task.generate_example()
    json.dumps(ex.metadata)


def test_both_labels_present():
    task = StratifiedReversalIntervention()
    labels = set()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(40):
            labels.add(task.generate_example().answer == IMPOSSIBLE)
    assert labels == {True, False}


def test_junk_and_empty_do_not_score_one():
    task = StratifiedReversalIntervention()
    for level in (0, 5):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("garbage input here", ex) < 1.0
        assert task.score_answer(None, ex) < 1.0
