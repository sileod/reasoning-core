import random

from math import gcd

from reasoning_core.template import Task
from reasoning_core.tasks.generated.manual_high_value_80_r1.modular_constraint_solver.modular_constraint_solver import (
    ModularConstraintSolver, _norm,
)


def _fresh_task(level=0):
    t = ModularConstraintSolver()
    t.config.set_level(level)
    return t


def test_generate_and_score_roundtrip():
    t = _fresh_task()
    for _ in range(50):
        x = t.generate_example()
        assert x.answer is not None
        assert t.score_answer(x.answer, x) == 1.0


def test_metadata_json_serializable():
    import json
    t = _fresh_task()
    for _ in range(20):
        x = t.generate_example()
        json.dumps(x.metadata)  # must not raise


def test_answer_format():
    t = _fresh_task()
    for _ in range(40):
        x = t.generate_example()
        ans = x.answer
        assert ans == "inconsistent" or "mod" in _norm(ans)


def test_both_classes_present():
    t = _fresh_task()
    seen_inc = seen_cons = False
    for _ in range(60):
        ans = t.generate_example().answer
        if ans == "inconsistent":
            seen_inc = True
        else:
            seen_cons = True
    assert seen_inc and seen_cons


def test_consistency_verified():
    from sympy.ntheory.modular import solve_congruence
    t = _fresh_task()
    for _ in range(40):
        x = t.generate_example()
        cong = x.metadata["congruences"]
        residues = [int(s.split()[0]) for s in cong]
        moduli = [int(s.split()[-1]) for s in cong]
        sol = solve_congruence(*[(a, m) for a, m in zip(residues, moduli)])
        if x.metadata["consistent"]:
            assert sol is not None
            assert _norm(x.answer) == _norm("%d mod %d" % (int(sol[0]), int(sol[1])))
        else:
            assert sol is None


def test_wrong_answers_score_zero():
    t = _fresh_task()
    x = t.generate_example()
    assert t.score_answer("", x) == 0.0
    assert t.score_answer("garbage", x) == 0.0


def test_difficulty_changes_config():
    t = _fresh_task()
    base = (t.config.n_cong, t.config.max_mod)
    t.config.set_level(5)
    hi = (t.config.n_cong, t.config.max_mod)
    assert hi[0] >= base[0] and hi[1] >= base[1]


def test_generate_is_seeded_reproducible():
    random.seed(12345)
    t1 = ModularConstraintSolver()
    first = [t1.generate_example().answer for _ in range(10)]
    random.seed(12345)
    t2 = ModularConstraintSolver()
    second = [t2.generate_example().answer for _ in range(10)]
    assert first == second


def test_canonical_residue_is_smallest_nonnegative():
    from sympy.ntheory.modular import solve_congruence
    for level in (0, 2, 5):
        t = _fresh_task(level)
        for _ in range(30):
            x = t.generate_example()
            if not x.metadata["consistent"]:
                continue
            cong = x.metadata["congruences"]
            residues = [int(s.split()[0]) for s in cong]
            moduli = [int(s.split()[-1]) for s in cong]
            sol, M = solve_congruence(*[(a, m) for a, m in zip(residues, moduli)])
            parts = x.answer.split()
            r, mm = int(parts[0]), int(parts[2])
            assert (r, mm) == (int(sol), int(M))
            assert 0 <= r < mm
            for candidate in range(r):
                assert not all(candidate % m == a for a, m in zip(residues, moduli))


def test_all_levels_generate():
    for level in (0, 1, 2, 3, 4, 5, 6):
        t = _fresh_task(level)
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1.0


def test_non_coprime_and_coprime_mix():
    t = _fresh_task()
    saw_non_coprime = False
    for _ in range(30):
        x = t.generate_example()
        cong = x.metadata["congruences"]
        moduli = [int(s.split()[-1]) for s in cong]
        if any(gcd(moduli[i], moduli[j]) > 1
               for i in range(len(moduli)) for j in range(i + 1, len(moduli))):
            saw_non_coprime = True
            break
    assert saw_non_coprime
