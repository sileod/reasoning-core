import random

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.coalitional_payoff_stability.coalitional_payoff_stability import (
    CoalitionalPayoffStability,
)


def _entry_at(level, seed):
    random.seed(seed)
    task = CoalitionalPayoffStability()
    task.config.set_level(level)
    return task, task.generate_entry()


def test_gold_answer_scores_one_across_levels():
    for level in (0, 2, 5):
        for seed in range(20):
            task, entry = _entry_at(level, seed)
            assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_below_one():
    for level in (0, 2, 5):
        for seed in range(20):
            task, entry = _entry_at(level, seed)
            for bad in ("", " ", "yes maybe", "[a, b]", "12", "no!!", "[3 7]"):
                assert task.score_answer(bad, entry) < 1.0


def test_exists_answers_are_yes_or_no():
    for level in (0, 2, 5):
        for seed in range(30):
            task, entry = _entry_at(level, seed)
            if entry.metadata["mode"] == "exists":
                assert entry.answer in ("yes", "no")


def test_range_answer_format():
    for level in (0, 2, 5):
        for seed in range(30):
            task, entry = _entry_at(level, seed)
            if entry.metadata["mode"] == "range":
                parts = entry.answer[1:-1].split(",")
                assert len(parts) == 2
                assert int(parts[0]) <= int(parts[1])
                assert entry.metadata["lo"][0] <= int(parts[0])
                assert int(parts[1]) <= entry.metadata["hi"][0]


def test_difficulty_changes_config():
    task = CoalitionalPayoffStability()
    task.config.set_level(0)
    base = task.config.n
    task.config.set_level(6)
    assert task.config.n > base


def test_metadata_json_roundtrip():
    import json
    for seed in range(10):
        _, entry = _entry_at(3, seed)
        json.dumps(entry.metadata)
