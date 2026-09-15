import random

from reasoning_core.tasks.generated.wave12.consensus_log_commit.consensus_log_commit import (
    ConsensusLogCommit,
    _score_integer,
    majority_commit_index,
)


def test_gold_scores_one():
    task = ConsensusLogCommit()
    for _ in range(20):
        task.config.set_level(random.randint(0, 6))
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_wrong_score_zero():
    task = ConsensusLogCommit()
    task.config.set_level(3)
    x = task.generate_example()
    expected = int(x.answer)
    wrong = expected + 0 if expected == 12345 else (expected + 1)
    if suggested := wrong_answer(expected):
        assert task.score_answer(str(suggested), x) == 0.0


def wrong_answer(expected):
    if expected >= 1:
        return expected + 1
    return expected + 1


def test_levels_vary_answer():
    task = ConsensusLogCommit()
    answers = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_example()
            answers.add(x.answer)
    assert len(answers) > 1


def test_none_global_reseed():
    import reasoning_core.tasks.generated.wave12.consensus_log_commit.consensus_log_commit as m

    task = m.ConsensusLogCommit()
    task.config.set_level(2)
    random.seed(0)
    a1 = task.generate_example().answer
    random.seed(0)
    a2 = task.generate_example().answer
    assert a1 == a2


def test_majority_math():
    positions = [1, 2, 5, 5, 6]
    assert majority_commit_index(5, 3, positions) == 5
    positions2 = [2, 3, 3]
    assert majority_commit_index(3, 2, positions2) == 3


def test_score_integer():
    assert _score_integer("5", "5") == 1.0
    assert _score_integer(" 5 ", "5") == 1.0
    assert _score_integer("4", "5") == 0.0
    assert _score_integer("junk", "5") == 0.0
    assert _score_integer("", "5") == 0.0


def test_validate():
    task = ConsensusLogCommit()
    task.validate()
