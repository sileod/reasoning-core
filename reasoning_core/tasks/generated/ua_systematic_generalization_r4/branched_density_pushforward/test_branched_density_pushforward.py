from fractions import Fraction

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.branched_density_pushforward.branched_density_pushforward import (
    BranchedDensityPushforward,
    _canonical,
    _continuous_mass,
    _format_answer,
    _integral_segs,
    _pushforward,
)


def test_identity_preserves_density():
    p = [(Fraction(0), Fraction(1), Fraction(2, 3))]
    ident = [(Fraction(0), Fraction(1), Fraction(1), Fraction(0))]
    q, atoms = _pushforward(p, ident)
    assert atoms == []
    assert _continuous_mass(q) == _integral_segs(p) == Fraction(2, 3)
    assert all(v == Fraction(2, 3) for (_a, _b, v) in q)


def test_mass_conserved_on_tent_map():
    p = [(Fraction(0), Fraction(1), Fraction(4, 5))]
    tent = [
        (Fraction(0), Fraction(1, 2), Fraction(2), Fraction(0)),
        (Fraction(1, 2), Fraction(1), Fraction(-2), Fraction(2)),
    ]
    q, atoms = _pushforward(p, tent)
    assert atoms == []
    assert _continuous_mass(q) == Fraction(4, 5)


def test_flat_branch_makes_atom():
    p = [(Fraction(0), Fraction(1), Fraction(1, 2))]
    flat = [(Fraction(0), Fraction(1), Fraction(0), Fraction(1, 3))]
    q, atoms = _pushforward(p, flat)
    assert q == []
    assert atoms == [(Fraction(1, 3), Fraction(1, 2))]


def test_gold_scores_and_survives_roundtrip():
    task = BranchedDensityPushforward()
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1


def test_junk_scores_zero():
    task = BranchedDensityPushforward()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0
    assert task.score_answer("reajrjrje9595!", entry) == 0
    assert task.score_answer("1,2,3", entry) != 1


def test_answer_reduced_form_matches():
    assert _canonical("2/4,0|2/6:1/4") == _canonical("1/2,0|1/3:1/4")


def test_all_levels_generate_and_score():
    task = BranchedDensityPushforward()
    for lev in (0, 1, 2, 3, 4, 5, 6):
        entry = task.generate_example(level=lev)
        assert task.score_answer(entry.answer, entry) == 1


def test_level_changes_config():
    task = BranchedDensityPushforward()
    c0 = task.config.to_dict()
    task.config.set_level(4)
    assert task.config.to_dict() != c0


def test_validate_passes():
    task = BranchedDensityPushforward()
    task.validate(n_samples=3)
