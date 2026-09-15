import random

from reasoning_core.template import Config, Entry, Task

random.seed(2267388306)

MODULE = "reasoning_core.tasks.generated.k3_dependence_relevance_r1.checksum_scheme_inference.checksum_scheme_inference"
import importlib

m = importlib.import_module(MODULE)


def test_discovery():
    assert m.ChecksumSchemeInference is not None
    from reasoning_core.template import Task
    assert issubclass(m.ChecksumSchemeInference, Task)


def test_gold_scores_one():
    task = m.ChecksumSchemeInference()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    task = m.ChecksumSchemeInference()
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("zzzz", e) == 0.0


def test_level_variety():
    task = m.ChecksumSchemeInference()
    seen = set()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(5):
            e = task.generate_example()
            seen.add(e.metadata["modulus"])
    assert seen == {7, 9, 11, 13}


def test_answer_domain():
    task = m.ChecksumSchemeInference()
    for _ in range(30):
        e = task.generate_example()
        assert e.answer in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
