import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))))

from reasoning_core.tasks.generated.k3_relational_structures_r1.cartesian_tree_construction.cartesian_tree_construction import CartesianTreeConstruction  # noqa: E402

random.seed(2267388306)


def test_generates_and_scores():
    task = CartesianTreeConstruction()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_garbage_scores_zero():
    task = CartesianTreeConstruction()
    task.config.set_level(3)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("0 0 0", ex) < 1.0
    assert task.score_answer(None, ex) == 0.0


def test_metadata_json_serializable():
    import json
    task = CartesianTreeConstruction()
    task.config.set_level(5)
    ex = task.generate_example()
    json.dumps(ex.metadata)


def test_difficulty_changes_config():
    task = CartesianTreeConstruction()
    base = task.config.length
    task.config.set_level(6)
    assert task.config.length != base
