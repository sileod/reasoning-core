import random

from reasoning_core.tasks.generated.k3_counterfactual_r1.palindromic_tree_counts.palindromic_tree_counts import (
    PalindromicTreeCounts,
)


def test_round_trip_score_gold():
    task = PalindromicTreeCounts()
    for _ in range(200):
        entry = task.generate_entry()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_bad_answers_score_zero():
    task = PalindromicTreeCounts()
    for _ in range(100):
        entry = task.generate_entry()
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("junk", entry) == 0.0
        assert task.score_answer("-1", entry) == 0.0


def test_count_matches_bruteforce():
    task = PalindromicTreeCounts()
    for _ in range(200):
        entry = task.generate_entry()
        text = entry.metadata["text"]
        query = entry.metadata["query"]
        expected = 0
        start = 0
        while True:
            idx = text.find(query, start)
            if idx == -1:
                break
            expected += 1
            start = idx + 1
        assert expected == entry.metadata["count"]
        assert str(expected) == entry.answer


def test_count_is_positive_and_query_is_palindrome():
    task = PalindromicTreeCounts()
    for _ in range(100):
        entry = task.generate_entry()
        query = entry.metadata["query"]
        assert query == query[::-1]
        assert entry.metadata["count"] >= 1


def test_occurrence_present_in_text():
    task = PalindromicTreeCounts()
    for _ in range(100):
        entry = task.generate_entry()
        assert entry.metadata["query"] in entry.metadata["text"]
        text = entry.metadata["text"]
        query = entry.metadata["query"]
        expected = 0
        start = 0
        while True:
            idx = text.find(query, start)
            if idx == -1:
                break
            expected += 1
            start = idx + 1
        assert entry.metadata["count"] == expected


def test_levels_change_config():
    task = PalindromicTreeCounts()
    config0 = task.config.__class__()
    config6 = task.config.__class__()
    config0.set_level(0)
    config6.set_level(6)
    assert config6.min_len >= config0.min_len
    assert config6.alphabet >= config0.alphabet
