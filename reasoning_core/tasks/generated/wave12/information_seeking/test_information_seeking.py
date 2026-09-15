import random

from reasoning_core.tasks.generated.wave12.information_seeking.information_seeking import (
    InformationSeeking,
)


def _best_split_seed():
    random.seed(42)
    task = InformationSeeking()
    task.config.set_level(1)
    for _ in range(50):
        entry = task.generate_example()
        assert entry.answer in entry.metadata["candidates"]
        # gold scores 1
        assert task.score_answer(entry.answer, entry) == 1.0
        # wrong name scores 0
        others = [n for n in entry.metadata["candidates"]
                  if n != entry.answer]
        assert task.score_answer(others[0], entry) == 0.0


def test_gold_scores_one():
    random.seed(1)
    task = InformationSeeking()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_and_empty():
    random.seed(2)
    task = InformationSeeking()
    task.config.set_level(3)
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0
    assert task.score_answer("Q9", entry) == 0.0


def test_answer_is_candidate():
    random.seed(3)
    task = InformationSeeking()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            entry = task.generate_example()
            assert entry.answer in entry.metadata["candidates"]


def test_balance_and_ticbreak():
    random.seed(4)
    task = InformationSeeking()
    task.config.set_level(1)
    for _ in range(100):
        entry = task.generate_example()
        cands = entry.metadata["candidates"]
        nh = entry.metadata["num_viable"]
        best_bal = min(
            abs(len(pos) - (nh - len(pos))) for pos in cands.values())
        chosen = entry.answer
        chosen_bal = abs(len(cands[chosen]) - (nh - len(cands[chosen])))
        assert chosen_bal == best_bal
        # tie-break: lexicographically smallest among those achieving best balance
        best_names = [n for n in cands
                      if abs(len(cands[n]) - (nh - len(cands[n]))) == best_bal]
        assert chosen == min(best_names)
