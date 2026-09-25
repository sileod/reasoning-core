import random

from reasoning_core.tasks.generated.ua_incremental_recomputation_r5.winding_region_repair.winding_region_repair import (
    WindingRegionRepair,
)


def test_gold_scores_one():
    random.seed(123)
    task = WindingRegionRepair()
    for _ in range(20):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_wrong_answers_fail():
    random.seed(456)
    task = WindingRegionRepair()
    for _ in range(20):
        x = task.generate_example()
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("junk", x) < 1.0
        assert task.score_answer("0:0;9:9", x) < 1.0


def test_difficulty_changes_config():
    task = WindingRegionRepair()
    task.config.set_level(0)
    l0 = task.config.n_vertices
    task.config.set_level(6)
    l6 = task.config.n_vertices
    assert l6 > l0


def test_metadata_json_serializable():
    import json

    random.seed(789)
    task = WindingRegionRepair()
    for _ in range(10):
        x = task.generate_example()
        json.dumps(x.metadata)
        assert isinstance(x.answer, str)


def test_answer_is_nonempty_at_all_levels():
    task = WindingRegionRepair()
    for level in range(7):
        task.config.set_level(level)
        random.seed(1000 + level)
        for _ in range(5):
            x = task.generate_example()
            assert x.answer != ""
