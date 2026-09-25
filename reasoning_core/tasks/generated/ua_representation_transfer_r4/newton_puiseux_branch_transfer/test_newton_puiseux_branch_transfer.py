import random

from reasoning_core.tasks.generated.ua_representation_transfer_r4.newton_puiseux_branch_transfer.newton_puiseux_branch_transfer import (
    NewtonPuiseuxBranchTransfer,
    NewtonPuiseuxConfig,
    _branch_to_factor,
    _build_factors,
    _poly_string,
)


def test_generate_and_score():
    task = NewtonPuiseuxBranchTransfer()
    for _ in range(200):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("zzz", entry) == 0.0
        assert int(entry.answer) == entry.metadata["ramification_index"] >= 1


def test_difficulty_changes_config():
    cfg = NewtonPuiseuxConfig()
    level0 = NewtonPuiseuxConfig()
    level0.set_level(0)
    level6 = NewtonPuiseuxConfig()
    level6.set_level(6)
    assert level0.n_factors < level6.n_factors
    assert level0.q_max < level6.q_max


def test_all_levels_generate():
    task = NewtonPuiseuxBranchTransfer()
    for level in range(0, 7):
        task.config.set_level(level)
        values = set()
        for _ in range(60):
            entry = task.generate_example()
            values.add(int(entry.answer))
            assert task.score_answer(entry.answer, entry) == 1.0
        assert len(values) >= 2, f"level {level} has constant-ish answers: {values}"


def test_branch_to_factor_consistency():
    random.seed(123)
    for _ in range(1000):
        factors = _build_factors(4, 5, 15)
        if factors is None:
            continue
        total = sum(q for _, q, _ in factors)
        for target in range(1, total + 1):
            p, q = _branch_to_factor(factors, target)
            running = 0
            found = None
            for pp, qq, _ in factors:
                running += qq
                if target <= running:
                    found = (pp, qq)
                    break
            assert found == (p, q)


def test_poly_string_unique():
    random.seed(7)
    for _ in range(200):
        factors = _build_factors(4, 5, 15)
        if factors is None:
            continue
        assert factors is not None
        s = _poly_string(factors)
        assert s.count(")(") == len(factors) - 1

    task = NewtonPuiseuxBranchTransfer()
    task.config.set_level(2)
    seen = set()
    for _ in range(100):
        e = task.generate_example()
        seen.add(e.metadata["polynomial"])
    assert len(seen) >= 50
