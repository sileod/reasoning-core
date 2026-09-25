import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.weighted_vote_realization.weighted_vote_realization import (
    WeightedVoteRealization,
    _bounds,
    _least_total,
    _realizable,
    _satisfies,
    _witness,
    score_realization,
)


@pytest.fixture(scope="module")
def task():
    return WeightedVoteRealization()


def test_gold_scores(task):
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_format(task):
    task.config.set_level(2)
    for _ in range(50):
        ex = task.generate_example()
        assert ex.answer in ("none",) or ex.answer.startswith("min:")


def test_impossible_variety(task):
    answers = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            answers.add(ex.answer)
    assert len(answers) > 1


def test_witness_valid(task):
    task.config.set_level(4)
    for _ in range(30):
        ex = task.generate_example()
        if ex.answer == "none":
            assert ex.metadata["feasible"] is False
        else:
            assert ex.metadata["feasible"] is True
            assert _witness(
                ex.metadata["weights_capacity"],
                ex.metadata["quota"],
                ex.metadata["labels"],
            ) is not None


def test_realizable_matches_feasibility(task):
    task.config.set_level(5)
    for _ in range(30):
        ex = task.generate_example()
        least = _least_total(
            ex.metadata["weights_capacity"],
            ex.metadata["quota"],
            ex.metadata["labels"],
        )
        feasible = least is not None and _realizable(
            ex.metadata["weights_capacity"],
            ex.metadata["quota"],
            ex.metadata["labels"],
            least,
        )
        assert feasible == (ex.answer != "none")
        if feasible:
            assert _satisfies(
                ex.metadata["weights_capacity"],
                ex.metadata["quota"],
                ex.metadata["labels"],
                _witness(
                    ex.metadata["weights_capacity"],
                    ex.metadata["quota"],
                    ex.metadata["labels"],
                ),
            )


def test_junk_and_empty_score_zero(task):
    task.config.set_level(3)
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage", ex) < 1.0
    assert task.score_answer("min:0", ex) <= 1.0
