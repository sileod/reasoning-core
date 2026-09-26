import random

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.graph_local_complement.task_graph_local_complementation import (
    GraphLocalComplementV1,
)


def test_generate_example():
    task = GraphLocalComplementV1()
    for level in range(7):
        task.config.set_level(level)
        x = task.generate_example()
        assert x.answer in ("yes", "no")
        assert isinstance(x.metadata["init_edges"], list)
        assert isinstance(x.metadata["sequence"], list)
        assert len(x.metadata["query"]) == 2


def test_roundtrip_scores():
    task = GraphLocalComplementV1()
    task.config.set_level(3)
    for _ in range(20):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
        other = "yes" if x.answer == "no" else "no"
        assert task.score_answer(other, x) < 1.0
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("junk", x) < 1.0


def test_answers_balanced():
    task = GraphLocalComplementV1()
    task.config.set_level(2)
    ones = 0
    total = 64
    for _ in range(total):
        x = task.generate_example()
        if x.answer == "yes":
            ones += 1
    excess = abs(ones - total / 2) / total
    assert excess < 0.35
