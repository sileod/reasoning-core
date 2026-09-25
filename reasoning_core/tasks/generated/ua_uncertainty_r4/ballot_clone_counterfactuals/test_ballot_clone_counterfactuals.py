import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.ballot_clone_counterfactuals.ballot_clone_counterfactuals import (
    BallotCloneCounterfactuals,
)


def test_generate_and_score():
    random.seed(1)
    task = BallotCloneCounterfactuals()
    for _ in range(20):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_junk_answers_fail():
    random.seed(2)
    task = BallotCloneCounterfactuals()
    x = task.generate_example()
    assert task.score_answer("junk", x) == 0.0
    assert task.score_answer("", x) == 0.0
    assert task.score_answer(x.answer + "x", x) == 0.0


def test_winners_valid_and_varied():
    random.seed(3)
    task = BallotCloneCounterfactuals()
    seen = set()
    for _ in range(30):
        x = task.generate_example()
        m = x.metadata
        assert set(m["winners"]).issubset(set(m["originals"]))
        assert len(m["winners"]) >= 1
        assert x.answer == "-".join(sorted(m["winners"]))
        seen.add(x.answer)
    assert len(seen) >= 2


def test_difficulty_scales():
    task = BallotCloneCounterfactuals()
    c0 = (task.config.k, task.config.voters, task.config.blocks)
    task.config.set_level(6)
    c6 = (task.config.k, task.config.voters, task.config.blocks)
    assert all(a >= b for a, b in zip(c6, c0))


def test_all_levels_generate():
    random.seed(5)
    task = BallotCloneCounterfactuals()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(5):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
