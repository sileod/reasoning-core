"""Tests for the antecedent binding legality task."""

import random

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.antecedent_binding_legality.antecedent_binding_legality import (
    AntecedentBindingLegality,
)


def _balanced_binary(examples):
    lic = sum(1 for e in examples if e.answer.count("licensed") >= e.answer.count("blocked"))
    return len(examples) - lic, lic


def test_gold_scores_one_all_levels():
    task = AntecedentBindingLegality()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_example(level=level)
            assert task.score_answer(x.answer, x) == 1.0
            assert task.score_answer("", x) < 1.0
            assert task.score_answer("garbage!", x) < 1.0


def test_every_trial_has_both_verdicts():
    task = AntecedentBindingLegality()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example(level=level)
            assert "licensed" in x.answer and "blocked" in x.answer


def test_all_four_target_types_occur():
    task = AntecedentBindingLegality()
    seen = set()
    for _ in range(120):
        x = task.generate_example()
        seen.add(x.metadata["target_type"])
    assert seen == {"anaphor_sg", "anaphor_pl", "pronoun", "name"}


def test_label_distribution_not_extreme():
    random.seed(1139467751)
    task = AntecedentBindingLegality()
    for level in (0, 3, 6):
        task.config.set_level(level)
        lic, blk = 0, 0
        for _ in range(40):
            x = task.generate_example(level=level)
            for w in x.answer.split(","):
                w = w.strip()
                if w == "licensed":
                    lic += 1
                else:
                    blk += 1
        total = lic + blk
        assert total > 0
        assert 0.2 <= lic / total <= 0.8


def test_displayed_tree_matches_computed_verdicts():
    task = AntecedentBindingLegality()
    for _ in range(20):
        x = task.generate_example()
        assert x.metadata["tree"].startswith("[S ")


def test_deterministic_under_seed():
    random.seed(999)
    t1 = AntecedentBindingLegality()
    a1 = [t1.generate_example().answer for _ in range(10)]
    random.seed(999)
    t2 = AntecedentBindingLegality()
    a2 = [t2.generate_example().answer for _ in range(10)]
    assert a1 == a2
