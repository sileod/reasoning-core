import random

from reasoning_core.tasks.generated.ua_global_over_greedy_r5.singular_residue_lift_survival.task_singular_residue_lift_survival import (
    SingularResidueLiftSurvival,
    _eval_mod,
    _lift_all,
    _roots_mod_p,
)


def test_generate_and_score():
    task = SingularResidueLiftSurvival()
    for _ in range(50):
        entry = task.generate_example()
        assert isinstance(entry.answer, str)
        assert 0.0 <= task.score_answer(entry.answer, entry) <= 1.0
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_correctness_via_verification():
    task = SingularResidueLiftSurvival()
    for _ in range(100):
        entry = task.generate_example()
        poly = entry.metadata["poly"]
        prime = entry.metadata["prime"]
        power = entry.metadata["power"]
        roots_mod_p = entry.metadata["roots_mod_p"]
        lifted = entry.metadata["lifted"]
        expected = sorted(set(_lift_all(poly, roots_mod_p, prime, power)))
        assert lifted == expected
        for r in lifted:
            assert _eval_mod(poly, r, prime ** power) == 0


def test_singular_roots_excluded():
    task = SingularResidueLiftSurvival()
    for _ in range(100):
        entry = task.generate_example()
        poly = entry.metadata["poly"]
        prime = entry.metadata["prime"]
        power = entry.metadata["power"]
        roots_mod_p = entry.metadata["roots_mod_p"]
        deriv = lambda r: sum(i * c * (r ** (i - 1)) for i, c in enumerate(poly) if i > 0)
        for r in roots_mod_p:
            if deriv(r) % prime == 0:
                for l in entry.metadata["lifted"]:
                    assert l % prime != r


def test_empty_answer_format():
    task = SingularResidueLiftSurvival()
    entry = task.generate_example()
    gold = entry.answer
    if gold == "none":
        assert task.score_answer("none", entry) == 1.0
        assert task.score_answer("", entry) == 0.0
    else:
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("junk", entry) == 0.0


def test_difficulty_changes_config():
    task = SingularResidueLiftSurvival()
    task.config.set_level(0)
    l0 = (task.config.max_degree, task.config.max_power)
    task.config.set_level(6)
    l6 = (task.config.max_degree, task.config.max_power)
    assert l6 != l0


def test_deterministic_seeded():
    random.seed(12345)
    task = SingularResidueLiftSurvival()
    a = task.generate_example().answer
    random.seed(12345)
    task2 = SingularResidueLiftSurvival()
    b = task2.generate_example().answer
    assert a == b


def test_brute_force_crosscheck_mod_power_small():
    task = SingularResidueLiftSurvival()
    task.config.set_level(0)
    task.config.max_prime = 29
    for _ in range(200):
        entry = task.generate_example()
        poly = entry.metadata["poly"]
        prime = entry.metadata["prime"]
        power = entry.metadata["power"]
        mod = prime ** power
        brute = sorted(r for r in range(mod) if sum(c * (r ** i) for i, c in enumerate(poly)) % mod == 0)
        assert entry.metadata["lifted"] == brute


def test_variety_of_survivor_counts():
    task = SingularResidueLiftSurvival()
    seen_multi = seen_single = False
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(200):
            entry = task.generate_example()
            lifted = entry.metadata["lifted"]
            if len(lifted) >= 2:
                seen_multi = True
            elif len(lifted) == 1:
                seen_single = True
    assert seen_multi and seen_single
