import random

from reasoning_core.tasks.generated.ua_inference_modes_r4.recursive_equivalence_extraction.recursive_equivalence_extraction import (
    RecursiveEquivalenceExtraction,
    min_cost,
    make_opdefs,
)


def test_roundtrip_all_levels():
    task = RecursiveEquivalenceExtraction()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert ex.metadata["min_cost"] > 0
        assert ex.metadata["target"] != ex.metadata["min_cost"]


def test_surface_safety():
    task = RecursiveEquivalenceExtraction()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        ans = ex.metadata["min_cost"]
        surface = {ex.metadata["target"], ex.metadata["maxv"]}
        surface.update(ex.metadata["atoms"])
        for o in ex.metadata["operators"]:
            surface.add(o["cost"])
            surface.add(o["budget"])
        assert ans not in surface


def test_scoring_rejects_junk():
    task = RecursiveEquivalenceExtraction()
    task.config.set_level(3)
    ex = task.generate_example()
    for bad in ["", "abc", "1.5", "[]", "None", "-3"]:
        assert task.score_answer(bad, ex) == 0.0


def test_min_cost_reference():
    opdefs = make_opdefs((1, 1, 2), (4, 2, 2), 8)
    assert min_cost([0, 1], 2, opdefs, 8, 6) == 1
    assert min_cost([0, 1], 0, opdefs, 8, 6) == 0


def test_balanced_bytes_reproducible():
    random.seed(368817805)
    t1 = RecursiveEquivalenceExtraction()
    t1.config.set_level(2)
    a = "|".join(t1.generate_example().answer for _ in range(20))
    random.seed(368817805)
    t2 = RecursiveEquivalenceExtraction()
    t2.config.set_level(2)
    b = "|".join(t2.generate_example().answer for _ in range(20))
    assert a == b
