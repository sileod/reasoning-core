import random

from reasoning_core.tasks.generated.ua_representation_specific_r4.set_family_shattering.set_family_shattering import (
    SetFamilyShattering,
)


def test_generate_and_score():
    random.seed(729651269)
    task = SetFamilyShattering()
    for _ in range(200):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
        assert x.answer in {
            "shatter",
            "not-shatter",
            "strong-shatter",
            "not-strong-shatter",
            "missing-trace",
        }


def test_junk_scores_zero():
    random.seed(1)
    task = SetFamilyShattering()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer(None, x) == 0.0


def test_difficulty_changes_config():
    task = SetFamilyShattering()
    task.config.set_level(0)
    base = task.config.ground_size
    task.config.set_level(6)
    high = task.config.ground_size
    assert high > base


def test_all_levels_generate_and_label_diversity():
    random.seed(729651269)
    task = SetFamilyShattering()
    seen = set()
    for level in (0, 2, 4, 6):
        task.config.set_level(level)
        for _ in range(60):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            seen.add((level, x.metadata["query"], x.answer))
    strong_pos = {k for k in seen if k[2] == "strong-shatter"}
    assert strong_pos, "strong-shatter positive label never occurs"


def test_label_balance_overall():
    random.seed(42)
    task = SetFamilyShattering()
    from collections import Counter

    counts = Counter()
    for _ in range(500):
        counts[task.generate_example().answer] += 1
    assert len(counts) >= 2
    top = max(counts.values())
    assert top / sum(counts.values()) < 0.8

