import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r5.heap_assertion_separability.heap_assertion_separability import (
    HeapAssertionSeparability,
)

MOD = Path(__file__)


def test_gold_scores_one():
    random.seed(12345)
    task = HeapAssertionSeparability()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer(task.render_prompt(ex.metadata), ex) is not None
            assert ex.answer in ("true", "false")


def test_bad_answers_do_not_score_one():
    random.seed(999)
    task = HeapAssertionSeparability()
    task.config.set_level(3)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0
    opposite = "false" if ex.answer == "true" else "true"
    assert task.score_answer(opposite, ex) == 0.0


def test_difficulty_changes_config():
    task = HeapAssertionSeparability()
    task.config.set_level(0)
    lo = task.config.max_cells
    task.config.set_level(6)
    hi = task.config.max_cells
    assert hi > lo


def test_balanced_truth_over_many_samples():
    random.seed(7)
    task = HeapAssertionSeparability()
    task.config.set_level(4)
    counts = {True: 0, False: 0}
    for _ in range(300):
        ex = task.generate_example()
        counts[bool(ex.metadata["answer_value"])] += 1
    tot = counts[True] + counts[False]
    assert 0.35 < counts[True] / tot < 0.65, counts


def test_both_labels_producible_at_every_level():
    task = HeapAssertionSeparability()
    for level in (0, 1, 2, 3, 4, 5, 6):
        random.seed(100 + level)
        task.config.set_level(level)
        saw = {True: False, False: False}
        for _ in range(60):
            ex = task.generate_example()
            saw[bool(ex.metadata["answer_value"])] = True
            if all(saw.values()):
                break
        assert all(saw.values()), (level, saw)


def test_metadata_json_serializable():
    import json

    task = HeapAssertionSeparability()
    task.config.set_level(3)
    ex = task.generate_example()
    json.dumps(ex.metadata)
    assert ex.metadata["universe"] > 0
    assert isinstance(ex.metadata["heap"], list)

