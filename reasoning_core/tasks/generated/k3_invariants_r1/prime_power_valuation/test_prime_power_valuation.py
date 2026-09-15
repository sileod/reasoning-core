import random

from reasoning_core.tasks.generated.k3_invariants_r1.prime_power_valuation.prime_power_valuation import (
    PrimePowerValuation,
    PrimePowerValuationConfig,
    _v_p_factorial,
    _v_p_double_factorial,
    _is_prime,
)


def test_smoke_default():
    random.seed(1)
    task = PrimePowerValuation()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_wrong_answer_scores_zero():
    random.seed(2)
    task = PrimePowerValuation()
    x = task.generate_example()
    gold = int(x.answer)
    assert task.score_answer(str(gold + 3), x) == 0.0
    assert task.score_answer("notanumber", x) == 0.0
    assert task.score_answer("", x) == 0.0


def test_all_levels_generate():
    random.seed(3)
    task = PrimePowerValuation()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            assert int(x.answer) >= 0


def test_factorial_helper():
    assert _v_p_factorial(5, 2) == 3
    assert _v_p_factorial(10, 2) == 8
    assert _v_p_factorial(10, 5) == 2
    assert _v_p_factorial(6, 3) == 2


def test_double_factorial_helper():
    assert _v_p_double_factorial(6, 2) == 4
    assert _v_p_double_factorial(5, 2) == 0


def test_double_factorial_bruteforce():
    import math
    for m in range(2, 15):
        prod = 1
        x = m
        while x >= 1:
            prod *= x
            x -= 2
        for p in (2, 3, 5, 7):
            expected = 0
            t = prod
            while t % p == 0:
                t //= p
                expected += 1
            assert _v_p_double_factorial(m, p) == expected


def test_factorial_bruteforce():
    import math
    for n in range(2, 15):
        for p in (2, 3, 5, 7, 11, 13):
            expected = 0
            t = math.factorial(n)
            while t % p == 0:
                t //= p
                expected += 1
            assert _v_p_factorial(n, p) == expected


def test_primes_used():
    random.seed(4)
    task = PrimePowerValuation()
    for _ in range(50):
        x = task.generate_example()
        assert _is_prime(x.metadata["p"])
        assert int(x.answer) >= 0


def test_level0_variety():
    random.seed(5)
    task = PrimePowerValuation()
    task.config.set_level(0)
    seen = set()
    for _ in range(60):
        x = task.generate_example()
        seen.add(x.metadata["mode"])
    assert seen == {"factorial", "binomial", "doublefact"}


def test_config_scaling():
    c = PrimePowerValuationConfig()
    c.set_level(0)
    assert c.max_n < PrimePowerValuationConfig().max_n


def test_validate():
    task = PrimePowerValuation()
    task.validate()
