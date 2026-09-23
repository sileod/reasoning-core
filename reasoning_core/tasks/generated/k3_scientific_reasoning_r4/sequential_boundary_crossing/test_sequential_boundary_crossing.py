"""Tests for sequential_boundary_crossing."""

import random

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.sequential_boundary_crossing import (
    sequential_boundary_crossing as mod,
)


def test_gold_scores_one():
    t = mod.SequentialBoundaryCrossing()
    for _ in range(50):
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1.0
    assert mod.SequentialBoundaryCrossing.design_choice.startswith(
        "Vary the number of looks"
    )


def test_garbage_does_not_score_one():
    t = mod.SequentialBoundaryCrossing()
    for _ in range(20):
        x = t.generate_example()
        assert t.score_answer("", x) == 0.0
        assert t.score_answer("garbage", x) == 0.0
        assert t.score_answer(123, x) == 0.0


def test_difficulty_changes_config():
    t = mod.SequentialBoundaryCrossing()
    c0 = t.config_cls()
    c0.set_level(0)
    c6 = t.config_cls()
    c6.set_level(6)
    assert c0.num_looks >= 2
    assert c0.num_looks <= c6.num_looks + 0


def test_summary_is_single_line():
    s = mod.SequentialBoundaryCrossing.summary
    assert isinstance(s, str)
    assert "\n" not in s
    assert len(s) > 40


def test_answer_domain():
    t = mod.SequentialBoundaryCrossing()
    for _ in range(30):
        x = t.generate_example()
        look, decision = x.answer.split()
        assert decision in ("efficacy", "futility", "continue")
        assert 1 <= int(look) <= x.metadata["num_looks"]


def test_label_balance_broad():
    random.seed(7)
    t = mod.SequentialBoundaryCrossing()
    from collections import Counter

    counts = Counter()
    for _ in range(300):
        x = t.generate_example()
        counts[x.metadata["decision"]] += 1
    assert counts["efficacy"] > 0
    assert counts["continue"] > 0
    assert counts["futility"] > 0
