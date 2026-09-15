import random

from reasoning_core.tasks.generated.k3_systematic_generalization_r1.skyline_dominance_query.skyline_dominance_query import SkylineDominanceQuery


def test_roundtrip():
    task = SkylineDominanceQuery()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_format():
    task = SkylineDominanceQuery()
    for _ in range(20):
        entry = task.generate_example()
        labels = entry.answer.split(",")
        for lab in labels:
            assert lab.strip().isdigit()
        assert labels == sorted(labels, key=int)


def test_garbage_scores_zero():
    task = SkylineDominanceQuery()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("abc", entry) == 0.0
    assert task.score_answer("999", entry) == 0.0


def test_label_surface_not_directly_answer():
    task = SkylineDominanceQuery()
    for _ in range(30):
        entry = task.generate_example()
        n = len(entry.metadata["points"])
        if n == 1:
            continue
        frontier = entry.answer.split(",")
        assert len(frontier) > 0 and len(frontier) <= n
        assert len(set(frontier)) == len(frontier)


def test_deterministic_seed():
    random.seed(12345)
    a = SkylineDominanceQuery().generate_example().answer
    random.seed(12345)
    b = SkylineDominanceQuery().generate_example().answer
    assert a == b
