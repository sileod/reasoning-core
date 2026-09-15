import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tree_reroot_distances import (
    TreeRerootDistances,
    _independent_total,
)


def test_generate_example():
    random.seed(1)
    task = TreeRerootDistances()
    task.config.set_level(0)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_answer_matches_independent_bfs_every_level():
    random.seed(2)
    task = TreeRerootDistances()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(15):
            x = task.generate_example()
            for q in range(x.metadata["n"]):
                tot = x.metadata["answer_value"] if q == x.metadata["query"] else None
            assert x.answer == str(x.metadata["answer_value"])
            assert _independent_total(
                x.metadata["n"], x.metadata["edges"], x.metadata["query"]
            ) == int(x.answer)
            assert int(x.answer) >= 0


def test_wrong_and_empty_score_zero():
    random.seed(3)
    task = TreeRerootDistances()
    task.config.set_level(2)
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    correct = x.answer
    wrong = str(int(correct) + 1)
    assert task.score_answer(wrong, x) == 0.0


def test_difficulty_scales():
    task = TreeRerootDistances()
    task.config.set_level(0)
    lo0, hi0 = task.config.node_range
    task.config.set_level(6)
    lo6, hi6 = task.config.node_range
    assert hi6 > hi0
    assert lo6 > lo0


def test_varied_answers():
    random.seed(7)
    task = TreeRerootDistances()
    task.config.set_level(3)
    answers = set()
    for _ in range(50):
        answers.add(task.generate_example().answer)
    assert len(answers) > 5


def test_config_resets_and_design_choice():
    assert TreeRerootDistances.design_choice.startswith(
        "Return only the rerooted total distance"
    )
    task = TreeRerootDistances()
    task.config.set_level(4)
    lo4, hi4 = task.config.node_range
    assert hi4 > lo4
