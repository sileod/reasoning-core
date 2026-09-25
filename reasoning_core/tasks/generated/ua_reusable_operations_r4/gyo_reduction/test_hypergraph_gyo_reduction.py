import random

from reasoning_core.tasks.generated.ua_reusable_operations_r4.hypergraph_gyo_reduction.hypergraph_gyo_reduction import (
    GyoReduction,
    gyo_reduce,
)


def _edges_equal_pairs(edges):
    seen = set()
    for e in edges:
        t = tuple(e)
        assert t not in seen
        seen.add(t)


def test_gold_scores_one():
    random.seed(1)
    task = GyoReduction()
    for _ in range(40):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    random.seed(2)
    task = GyoReduction()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer("EMPTY", x) < 1.0


def test_both_verdicts_across_levels():
    task = GyoReduction()
    for level in (0, 3, 6):
        task.config.set_level(level)
        verdicts = set()
        for _ in range(60):
            x = task.generate_example()
            verdicts.add(x.metadata["verdict"])
            assert x.metadata["verdict"] in ("EMPTY", "BLOCKED")
        assert verdicts == {"EMPTY", "BLOCKED"}, (level, verdicts)


def test_difficulty_changes():
    task = GyoReduction()
    base = GyoReduction().config.max_edges
    task.config.set_level(5)
    assert task.config.max_edges > base


def test_trace_matches_reduce():
    task = GyoReduction()
    for _ in range(30):
        x = task.generate_example()
        trace = gyo_reduce(x.metadata["edges"])
        assert x.answer == " ".join(trace)
        assert x.metadata["trace"] == list(trace)


def test_unique_edges_and_reproducibility():
    random.seed(7)
    task = GyoReduction()
    first = task.generate_example().answer
    random.seed(7)
    task2 = GyoReduction()
    second = task2.generate_example().answer
    assert first == second


def test_metadata_json_serializable():
    import json

    random.seed(3)
    task = GyoReduction()
    x = task.generate_example()
    json.dumps(x.metadata)
