from fractions import Fraction

from reasoning_core.tasks.generated.k3_verification_repair_r1.shortest_path_betweenness.shortest_path_betweenness import (
    ShortestPathBetweenness,
    _brandes_betweenness,
    _brute_betweenness,
)


def test_roundtrip_consistent():
    for level in (0, 2, 5):
        task = ShortestPathBetweenness()
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert ex.answer == ex.metadata["betweenness"]


def test_answer_is_rational():
    for level in (0, 2, 5):
        task = ShortestPathBetweenness()
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            num, den = ex.answer.split("/")
            f = Fraction(int(num), int(den))
            assert Fraction(int(num), int(den)) == f
            assert den != "0"


def test_score_rejects_junk():
    task = ShortestPathBetweenness()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("not a fraction", ex) == 0.0
    assert task.score_answer("1/0", ex) == 0.0


def test_brute_matches_brandes():
    task = ShortestPathBetweenness()
    ex = task.generate_example()
    b = _brandes_betweenness(ex.metadata["adjacency"], ex.metadata["nodes"], ex.metadata["target"])
    g = _brute_betweenness(ex.metadata["adjacency"], ex.metadata["nodes"], ex.metadata["target"])
    assert b == g
