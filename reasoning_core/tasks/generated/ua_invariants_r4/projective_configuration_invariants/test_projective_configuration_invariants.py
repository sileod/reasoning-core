from fractions import Fraction

from reasoning_core.tasks.generated.ua_invariants_r4.projective_configuration_invariants.projective_configuration_invariants import (
    ProjectiveConfigurationInvariants,
    _parse_frac,
    _solve_unknown,
    _cr_frac,
)


def test_gold_scores_one():
    task = ProjectiveConfigurationInvariants()
    for _ in range(50):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    task = ProjectiveConfigurationInvariants()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("abc", x) == 0.0
    assert task.score_answer("1/0", x) == 0.0


def test_answer_format_reduced():
    task = ProjectiveConfigurationInvariants()
    for _ in range(30):
        x = task.generate_example()
        f = _parse_frac(x.answer)
        assert str(f) == x.answer
        assert isinstance(f, Fraction)


def test_solver_roundtrip():
    import random as _r
    for _ in range(200):
        known = [_r.randint(-6, 6) for _ in range(3)]
        u = _r.randrange(4)
        all_vals = list(known)
        all_vals.insert(u, _r.randint(-6, 6))
        if len(set(all_vals)) != 4:
            continue
        t = _cr_frac(all_vals)
        if str(t) == "0/0":
            continue
        sol = _solve_unknown(known, u, t)
        assert sol is not None
        reconstructed = list(known)
        reconstructed.insert(u, sol)
        assert _cr_frac(reconstructed) == t


def test_difficulty_changes():
    task = ProjectiveConfigurationInvariants()
    base = task.config.max_mag
    task.config.set_level(6)
    assert task.config.max_mag > base
