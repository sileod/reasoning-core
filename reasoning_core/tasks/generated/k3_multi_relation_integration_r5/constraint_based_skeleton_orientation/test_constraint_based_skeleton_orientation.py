import random

from reasoning_core.tasks.generated.k3_multi_relation_integration_r5.constraint_based_skeleton_orientation.constraint_based_skeleton_orientation import (
    ConstraintBasedSkeletonOrientation,
)


def test_generate_and_score_gold():
    random.seed(1662004003)
    task = ConstraintBasedSkeletonOrientation()
    for _ in range(20):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_score_rejects_junk():
    random.seed(1662004003)
    task = ConstraintBasedSkeletonOrientation()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("garbage", x) < 1.0


def test_difficulty_changes_config():
    task = ConstraintBasedSkeletonOrientation()
    base = task.config.n_nodes
    task.config.set_level(4)
    assert task.config.n_nodes != base or task.config.n_ci > task.config.n_ci
