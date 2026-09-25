import random

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.optimality_theory_tableau_ranking.optimality_theory_tableau_ranking import (
    OptimalityTheoryTableauRanking,
    _winner,
)


def test_generate_and_score_roundtrip():
    random.seed(1234)
    task = OptimalityTheoryTableauRanking()
    for _ in range(200):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_winner_query_single_winner():
    random.seed(7)
    task = OptimalityTheoryTableauRanking()
    task.config.set_level(2)
    winners = 0
    for _ in range(200):
        ex = task.generate_example()
        if ex.metadata["query"] == "winner":
            winners += 1
            rows = [(lb, list(v)) for lb, v in ex.metadata["rows"]]
            assert _winner(rows, ex.metadata["ranking"]) == ex.answer


def test_all_query_types_present():
    random.seed(99)
    task = OptimalityTheoryTableauRanking()
    seen = set()
    for _ in range(1000):
        ex = task.generate_example()
        seen.add(ex.metadata["query"])
    assert seen == {"winner", "eliminated", "reranking"}


def test_levels_produce_examples():
    task = OptimalityTheoryTableauRanking()
    for level in range(7):
        task.config.set_level(level)
        random.seed(level + 1)
        for _ in range(30):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    random.seed(5)
    task = OptimalityTheoryTableauRanking()
    task.config.set_level(3)
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("   ", ex) == 0.0
        assert task.score_answer("xyz", ex) == 0.0


def test_eliminated_query_matches():
    random.seed(42)
    task = OptimalityTheoryTableauRanking()
    task.config.set_level(1)
    for _ in range(200):
        ex = task.generate_example()
        if ex.metadata["query"] == "eliminated":
            assert ex.answer == ",".join(sorted(ex.answer.split(",")))


def test_reranking_wrong_winner_zero():
    random.seed(3)
    task = OptimalityTheoryTableauRanking()
    task.config.set_level(4)
    for _ in range(50):
        ex = task.generate_example()
        if ex.metadata["query"] == "reranking":
            ranking = ex.metadata["ranking"]
            rows = [(lb, list(v)) for lb, v in ex.metadata["rows"]]
            assert _winner(rows, ranking) != _winner(rows, [int(x) for x in ex.answer.split(",")])
