import math
import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.measurement_uncertainty_propagation.measurement_uncertainty_propagation import (
    MeasurementUncertaintyPropagation,
    _propagate,
    _gradients,
    score_answer,
)


def _recompute(meta):
    leaves = [(lf["name"], lf["value"], lf["half_width"]) for lf in meta["leaves"]]
    nodes = [(nd["op"], nd["a"], nd["b"], nd["mode"]) for nd in meta["nodes"]]
    values, hwidths = _propagate(leaves, nodes)
    grads = _gradients(leaves, nodes, values)
    return leaves, nodes, values, hwidths, grads


def test_gold_scoring_all_levels():
    task = MeasurementUncertaintyPropagation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert score_answer(ex.answer, ex) == 1.0


def test_propagation_matches_recompute():
    task = MeasurementUncertaintyPropagation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            meta = ex.metadata
            leaves, nodes, values, hwidths, grads = _recompute(meta)
            nleaf = len(leaves)
            assert abs(values[-1] - meta["root_value"]) < 1e-9
            assert abs(hwidths[-1] - meta["root_hwidth"]) < 1e-9
            contribs = [abs(g) * lf[2] for g, lf in zip(grads, leaves)]
            dom = max(range(nleaf), key=lambda i: contribs[i])
            assert meta["dominant"] == leaves[dom][0]


def test_domain_and_junk():
    task = MeasurementUncertaintyPropagation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            if ex.metadata["regime"] == "dominant":
                assert score_answer("", ex) == 0.0
                assert score_answer("garbage", ex) == 0.0
            else:
                assert score_answer("", ex) == 0.0
                assert score_answer("not a number", ex) == 0.0


def test_random_score_zero():
    task = MeasurementUncertaintyPropagation()
    ex = task.generate_example()
    assert score_answer("Z", ex) == 0.0 if ex.metadata["regime"] == "dominant" else True


def test_balanced_labels():
    task = MeasurementUncertaintyPropagation()
    task.config.set_level(3)
    seen = set()
    for _ in range(60):
        ex = task.generate_example()
        seen.add(ex.metadata["regime"])
    assert seen == {"value", "hwidth", "dominant"}
