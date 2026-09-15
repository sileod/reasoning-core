import random

from reasoning_core.tasks.generated.k3_uncertainty_r1.counterfeit_weighing_deduction.counterfeit_weighing_deduction import (
    CounterfeitWeighingDeduction,
    candidate_set,
    format_candidates,
    predicted,
)


def test_generate_and_score():
    task = CounterfeitWeighingDeduction()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_answer_is_consistent_candidates():
    task = CounterfeitWeighingDeduction()
    for _ in range(50):
        x = task.generate_example()
        cands = candidate_set(x.metadata["n_coins"], [
            (w["left"], w["right"], w["outcome"]) for w in x.metadata["weighings"]
        ])
        assert format_candidates(cands) == x.answer


def test_hidden_in_answer():
    task = CounterfeitWeighingDeduction()
    for _ in range(50):
        x = task.generate_example()
        assert x.metadata["hidden"] in set(x.answer.split())


def test_answer_nonempty_and_bounded():
    task = CounterfeitWeighingDeduction()
    x = task.generate_example()
    parts = x.answer.split()
    assert len(parts) >= 1
    assert len(parts) <= 2 * x.metadata["n_coins"]


def test_garbage_does_not_score():
    task = CounterfeitWeighingDeduction()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("junk answer here", x) == 0.0
    assert task.score_answer(123, x) == 0.0
    assert task.score_answer("0H 1H", random.choice([x])) == 0.0 or x.answer != "0H 1H"


def test_difficulty_changes_config():
    task = CounterfeitWeighingDeduction()
    task.config.set_level(0)
    c0 = (task.config.n_coins, task.config.n_weighings)
    task.config.set_level(6)
    c6 = (task.config.n_coins, task.config.n_weighings)
    assert c0 != c6
    assert c6[0] > c0[0]
    assert c6[1] > c0[1]


def test_predicted_matches_recorded_for_hidden():
    task = CounterfeitWeighingDeduction()
    for _ in range(50):
        x = task.generate_example()
        assert predicted(
            x.metadata["weighings"][0]["left"],
            x.metadata["weighings"][0]["right"],
            int(x.metadata["hidden"][:-1]),
            1 if x.metadata["hidden"].endswith("H") else -1,
        ) == x.metadata["weighings"][0]["outcome"]
