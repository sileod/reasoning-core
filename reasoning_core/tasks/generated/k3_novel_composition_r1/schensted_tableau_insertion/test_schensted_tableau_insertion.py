import pytest

from reasoning_core.tasks.generated.k3_novel_composition_r1.schensted_tableau_insertion.schensted_tableau_insertion import (
    SchenstedTableauInsertion,
    encode_tableau,
    insert_symbol,
    verify_tableau,
)


def test_round_trip_scores():
    task = SchenstedTableauInsertion()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_garbage_scores_zero():
    task = SchenstedTableauInsertion()
    e = task.generate_example()
    assert task.score_answer("garbage", e) == 0.0
    assert task.score_answer("", e) == 0.0


def test_difficulty_changes_config():
    task = SchenstedTableauInsertion()
    task.config.set_level(0)
    w0 = task.config.width
    task.config.set_level(6)
    assert task.config.width > w0


def test_insertion_yields_valid_tableau():
    task = SchenstedTableauInsertion()
    for _ in range(100):
        e = task.generate_example()
        rows = [
            [int(x) for x in row.split(",")]
            for row in e.answer.split(";")
            if row != ""
        ]
        assert verify_tableau(rows)


def test_shape_decreasing():
    task = SchenstedTableauInsertion()
    for _ in range(100):
        e = task.generate_example()
        rows = [len(r.split(",")) for r in e.answer.split(";") if r != ""]
        assert all(rows[i] >= rows[i + 1] for i in range(len(rows) - 1))


def test_word_levels_vary():
    task = SchenstedTableauInsertion()
    task.config.set_level(0)
    answers0 = {task.generate_example().answer for _ in range(30)}
    task.config.set_level(6)
    answers6 = {task.generate_example().answer for _ in range(30)}
    assert len(answers0) > 1
    assert len(answers6) > 1


def test_insert_matches_replay():
    task = SchenstedTableauInsertion()
    for _ in range(100):
        e = task.generate_example()
        tab = []
        for s in e.metadata["word"]:
            tab = insert_symbol(tab, s)
        assert encode_tableau(tab) == e.answer

