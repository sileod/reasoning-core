import random

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.rooted_tree_series_composition.rooted_tree_series_composition import (
    RootedTreeSeriesComposition,
    cuts,
    brute_cuts,
    compose,
    aut_forest,
    canonical_string,
    random_canonical_tree,
    trees,
)
from fractions import Fraction


def test_roundtrip_score():
    t = RootedTreeSeriesComposition()
    e = t.generate_example()
    assert t.score_answer(e.answer, e) == 1.0
    assert t.score_answer("x", e) == 0.0
    assert t.score_answer("", e) == 0.0


def test_levels_produce_examples():
    t = RootedTreeSeriesComposition()
    for L in range(7):
        t.config.set_level(L)
        e = t.generate_example()
        assert e.answer != ""


def test_cuts_consistency_all_small_trees():
    for n in range(1, 6):
        for tr in trees(n):
            a = set(cuts(tr))
            b = brute_cuts(tr)
            assert a == b, f"mismatch for {canonical_string(tr)}"


def test_aut_forest():
    assert aut_forest(()) == 1
    assert aut_forest(((),)) == 1
    assert aut_forest(((), ())) == 2
    assert aut_forest(((), (), ())) == 6


def test_difficulty_changes_config():
    t = RootedTreeSeriesComposition()
    t.config.set_level(0)
    s0 = t.config.series_size
    t.config.set_level(6)
    assert t.config.series_size >= s0


def test_fraction_domain_valid():
    t = RootedTreeSeriesComposition()
    t.config.set_level(5)
    for _ in range(20):
        e = t.generate_example()
        num = e.metadata["coeff_num"]
        den = e.metadata["coeff_den"]
        assert den > 0
        assert Fraction(num, den) == Fraction(num, den)
