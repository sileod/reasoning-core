import random
import pytest

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.decision_tree_induction import (
    decision_tree_induction as module,
)
from reasoning_core.template import Task


def test_generate_scores():
    random.seed(1)
    task = module.DecisionTreeInduction()
    task.config.set_level(0)
    for _ in range(20):
        x = task.generate_example()
        assert module.score_answer(x.answer, x) == 1.0


def test_score_rejects_junk():
    random.seed(2)
    task = module.DecisionTreeInduction()
    x = task.generate_example()
    assert module.score_answer("", x) == 0.0
    assert module.score_answer("garbage", x) == 0.0


def test_verifier_reproduces_labels():
    random.seed(3)
    task = module.DecisionTreeInduction()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert module._evaluate(x.metadata["tree"], x.metadata["rows"]) == "ok"


def test_level6_generates():
    random.seed(9)
    task = module.DecisionTreeInduction()
    task.config.set_level(6)
    for _ in range(15):
        x = task.generate_example()
        assert module.score_answer(x.answer, x) == 1.0


def test_difficulty_changes_config():
    task = module.DecisionTreeInduction()
    task.config.set_level(0)
    assert task.config.n_rows == 10
    task.config.set_level(5)
    assert task.config.n_rows == 30


def test_metadata_json_serializable():
    import json

    task = module.DecisionTreeInduction()
    x = task.generate_example()
    json.dumps(x.metadata)


def test_validate():
    task = module.DecisionTreeInduction()
    task.validate()
