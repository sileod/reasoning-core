import random

import pytest

from reasoning_core.tasks.generated.ua_psychometrics_r4.perceptual_rivalry_adaptation.perceptual_rivalry_adaptation import (
    PerceptualRivalryAdaptation,
    _parse_answer,
    _simulate,
    _step,
)


def test_basic_example_roundtrip():
    task = PerceptualRivalryAdaptation()
    x = task.generate_example()
    assert x.answer in ("A", "B")
    assert task.score_answer(x.answer, x) == 1.0

    for bad in ("", " ", "C", "a b", "A B", "0", "A1", "AB", "13"):
        assert task.score_answer(bad, x) == 0.0
    for good in ("A", "a", "B", "b"):
        assert task.score_answer(good, x) == float(good.strip().upper() == x.answer)


def test_answer_within_domain():
    task = PerceptualRivalryAdaptation()
    for _ in range(200):
        x = task.generate_example()
        assert x.answer in ("A", "B")
        assert 0.0 <= x.metadata["final_A"] <= 1.0
        assert 0.0 <= x.metadata["final_B"] <= 1.0
        assert x.metadata["switch_count"] >= 0
        assert abs(x.metadata["final_A"] - x.metadata["final_B"]) >= 1e-9


def test_lineage_reproducible():
    random.seed(12345)
    task = PerceptualRivalryAdaptation()
    first = task.generate_example()
    random.seed(12345)
    task2 = PerceptualRivalryAdaptation()
    second = task2.generate_example()
    f1 = {k: v for k, v in dict(first.metadata).items() if not k.startswith("_")}
    f2 = {k: v for k, v in dict(second.metadata).items() if not k.startswith("_")}
    assert f1 == f2
    assert first.answer == second.answer


def test_step_keeps_activations_in_unit_interval():
    for _ in range(1000):
        x0 = random.random()
        y0 = random.random()
        w = random.uniform(0.05, 0.45)
        alpha = random.uniform(0.03, 0.3)
        rr = random.uniform(0.08, 0.45)
        kind = random.choice(("A", "B", "rest"))
        s = random.uniform(0.0, 0.8) if kind != "rest" else 0.0
        x1, y1 = _step(x0, y0, (kind, s), w, alpha, rr)
        assert 0.0 <= x1 <= 1.0
        assert 0.0 <= y1 <= 1.0


def test_simulate_consistent_with_step():
    x, y = 0.5, 0.5
    w, alpha, rr = 0.2, 0.15, 0.3
    pulses = [("A", 0.5), ("B", 0.3), ("rest", 0.0), ("A", 0.4)]
    doms, fx, fy = _simulate(x, y, w, alpha, rr, pulses, True)
    assert len(doms) == len(pulses)
    assert all(d in ("A", "B") for d in doms)


def test_parse_answer():
    assert _parse_answer("A") == "A"
    assert _parse_answer("b") == "B"
    assert _parse_answer(" B ") == "B"
    assert _parse_answer("C") is None
    assert _parse_answer(None) is None
    assert _parse_answer(5) is None


def test_difficulty_changes_config():
    t = PerceptualRivalryAdaptation()
    low = t.config.steps
    t.config.set_level(6)
    high = t.config.steps
    assert high > low


def test_label_variety_across_seed():
    counts = {"A": 0, "B": 0}
    random.seed(2024)
    task = PerceptualRivalryAdaptation()
    for _ in range(120):
        x = task.generate_example()
        counts[x.answer] += 1
    assert counts["A"] > 0 and counts["B"] > 0
