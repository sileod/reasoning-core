import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import random
import pytest

from hierarchical_knockout_compositing import (
    HierarchicalKnockoutCompositing, KnockoutConfig, _resolve_group,
    render_groups, build_groups)


def test_gold_scores_one():
    task = HierarchicalKnockoutCompositing()
    for _ in range(50):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    task = HierarchicalKnockoutCompositing()
    entry = task.generate_example()
    for bad in ["", "garbage", "1,2,3", "a,b,c,d,e", None]:
        assert task.score_answer(bad, entry) < 1.0


def test_difficulty_changes():
    c = KnockoutConfig()
    c.set_level(0)
    d0 = c.depth
    c.set_level(6)
    assert c.depth >= d0


def test_domain_bounds():
    task = HierarchicalKnockoutCompositing()
    for _ in range(30):
        groups = build_groups(task.config)
        res = render_groups(groups)
        for v in res:
            assert 0.0 <= v <= 1.0 + 1e-9


def test_resolve_composes_leaf():
    # a single leaf with mask 1 over transparent backdrop
    leaf = {'kind': 'leaf', 'alpha': 0.5, 'color': [1.0, 0.0, 0.0], 'mask': 1}
    pm, cov = _resolve_group(leaf, [0.0, 0.0, 0.0, 0.0], 0.0)
    assert abs(pm[0] - 0.5) < 1e-4
    assert abs(pm[3] - 0.5) < 1e-4
    assert abs(cov - 1.0) < 1e-4


def test_mask_zero_paints_nothing():
    leaf = {'kind': 'leaf', 'alpha': 0.9, 'color': [1.0, 1.0, 1.0], 'mask': 0}
    pm, cov = _resolve_group(leaf, [0.3, 0.3, 0.3, 1.0], 1.0)
    assert abs(cov - 1.0) < 1e-4
    assert abs(pm[3] - 1.0) < 1e-4
    assert abs(pm[0] - 0.3) < 1e-4
