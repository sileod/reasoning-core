import pytest

from reasoning_core.tasks.generated.wave12.termination_ranking_function.termination_ranking_function import (
    TerminationRankingFunction,
    TerminationRankingConfig,
    _find_ranking,
)


def _parse_coeffs(txt):
    return [int(x) for x in txt.split(",")]


def test_gold_answers_score_one():
    task = TerminationRankingFunction()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_entry()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = TerminationRankingFunction()
    task.config.set_level(3)
    ex = task.generate_entry()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage", ex) < 1.0
    assert task.score_answer("1,2,3,4,5,6,7", ex) < 1.0


def test_answer_is_real_ranking():
    task = TerminationRankingFunction()
    task.config.set_level(4)
    ex = task.generate_entry()
    coeffs = ex.metadata["coeffs"]
    c = _parse_coeffs(ex.answer)
    n = len(coeffs[0])
    assert len(c) == n
    for i in range(n):
        total = sum(c[j] * coeffs[i][j] for j in range(n))
        assert total <= -1
    assert all(abs(v) <= 5 for v in c)


def test_answer_changes_across_examples():
    task = TerminationRankingFunction()
    task.config.set_level(3)
    answers = {task.generate_entry().answer for _ in range(50)}
    assert len(answers) > 1


def test_difficulty_changes_nvars():
    task = TerminationRankingFunction()
    lows = []
    highs = []
    task.config.set_level(0)
    for _ in range(30):
        lows.append(task.generate_entry().metadata["coeffs"][0])
    task.config.set_level(6)
    for _ in range(30):
        highs.append(task.generate_entry().metadata["coeffs"])
    assert len(highs[0]) >= len(lows[0])


def test_find_ranking_correct():
    coeffs = [[-1, 1], [0, -1]]
    row, comb = _find_ranking(coeffs)
    assert row is not None
    for i in range(2):
        assert sum(row[j] * coeffs[i][j] for j in range(2)) <= -1


def test_validate():
    TerminationRankingFunction().validate()
