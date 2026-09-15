import random

from reasoning_core.tasks.generated.k3_representation_specific_r1.tower_block_removal.tower_block_removal import (
    TowerBlockRemoval,
    _simulate,
    _verify,
    _interface_fail,
)


def test_gold_scores_one():
    task = TowerBlockRemoval()
    for _ in range(30):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1


def test_junk_scores_zero():
    task = TowerBlockRemoval()
    entry = task.generate_example()
    for bad in ("", " ", "none 0", "reajrjrje9595!", "yes 5", "1,2,3"):
        if bad != entry.answer:
            assert task.score_answer(bad, entry) < 1


def test_height_domain():
    task = TowerBlockRemoval()
    for _ in range(40):
        entry = task.generate_example()
        assert isinstance(entry.metadata["height"], int)
        assert 1 <= entry.metadata["height"] <= entry.metadata["n"]
        assert all(isinstance(b, int) for b in entry.metadata["topple"])
        assert all(1 <= b <= entry.metadata["n"] for b in entry.metadata["topple"])


def test_verifier_independent():
    task = TowerBlockRemoval()
    for _ in range(40):
        entry = task.generate_example()
        n = entry.metadata["n"]
        w = entry.metadata["widths"]
        m = entry.metadata["masses"]
        X = entry.metadata["positions"]
        action = tuple(entry.metadata["action"])
        topple, survivors, Xa = _simulate(X, w, m, action, n)
        present = sorted(
            [i for i in range(n) if action[0] != "remove" or i != action[1]]
        )
        assert _verify(Xa, w, m, present, topple)
        assert [i + 1 for i in topple] == entry.metadata["topple"]
        assert len(survivors) == entry.metadata["height"]


def test_actions_vary():
    task = TowerBlockRemoval()
    actions = set()
    answers = set()
    for _ in range(60):
        entry = task.generate_example()
        actions.add(entry.metadata["action"][0])
        answers.add(entry.answer)
    assert {"remove", "nudge"} <= actions
    assert len(answers) > 1


def test_difficulty_changes_config():
    task = TowerBlockRemoval()
    task.config.set_level(0)
    low = (task.config.n_min, task.config.n_max)
    task.config.set_level(6)
    high = (task.config.n_min, task.config.n_max)
    assert low != high
