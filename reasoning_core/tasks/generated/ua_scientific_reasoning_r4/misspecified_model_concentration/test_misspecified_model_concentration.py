from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.misspecified_model_concentration.misspecified_model_concentration import (
    FAMILIES,
    MisspecifiedModelConcentration,
)


def test_gold_scores_1():
    task = MisspecifiedModelConcentration()
    for _ in range(200):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_0():
    task = MisspecifiedModelConcentration()
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("garbage", ex) == 0.0
        assert task.score_answer("Nonexistent", ex) == 0.0


def test_answer_is_valid_subset():
    task = MisspecifiedModelConcentration()
    seen = set()
    for _ in range(200):
        ex = task.generate_example()
        for name in ex.answer.split(","):
            assert name in FAMILIES
        assert ex.answer == ",".join(sorted(ex.answer.split(",")))
        seen.add(ex.answer)
    assert len(seen) >= 2


def test_survivors_are_argmax_elbo():
    task = MisspecifiedModelConcentration()
    for _ in range(150):
        ex = task.generate_example()
        els = ex.metadata["elbo"]
        best = max(els.values())
        survivors = sorted(f for f, v in els.items() if abs(best - v) <= 1e-6)
        assert ",".join(survivors) == ex.answer


def test_config_difficulty_changes():
    task = MisspecifiedModelConcentration()
    task.config.set_level(0)
    k0 = task.config.k
    task.config.set_level(6)
    k6 = task.config.k
    assert k6 >= k0


def test_domain_valid():
    task = MisspecifiedModelConcentration()
    for _ in range(100):
        ex = task.generate_example()
        g = ex.metadata["g"]
        assert abs(sum(g) - 1.0) < 1e-6
        assert all(0 < gi for gi in g)
        for v in ex.metadata["elbo"].values():
            assert v == v  # not NaN


def test_independent_recompute():
    """Recompute ELBOs by hand (independent of the module) and confirm survivors."""
    import math

    from scipy.optimize import minimize_scalar

    task = MisspecifiedModelConcentration()
    for _ in range(60):
        ex = task.generate_example()
        g = ex.metadata["g"]
        k = len(g)
        mean = sum(i * gi for i, gi in enumerate(g))

        # geometric: minimize -L over a in (0,1), L(a) = log(1-a) + mean*log(a)
        def neg_geo(loga):
            a = math.exp(min(max(loga, -25.0), -1e-9))
            return -(math.log(1.0 - a) + mean * math.log(a))

        geo = -minimize_scalar(neg_geo, bounds=(-25.0, -1e-8), method="bounded").fun

        # poisson closed form
        pois = mean * math.log(mean) - mean - sum(gi * math.lgamma(i + 1) for i, gi in enumerate(g))

        # rising: p(i) prop a^(k-1-i)
        jbar = (k - 1) - mean

        def neg_rise(loga):
            a = math.exp(min(max(loga, -25.0), -1e-9))
            Z = sum(a ** j for j in range(k))
            return -(jbar * math.log(a) - math.log(Z))

        rise = -minimize_scalar(neg_rise, bounds=(-25.0, -1e-8), method="bounded").fun

        els = {"Geometric": geo, "Poisson": pois, "Rising": rise}
        best = max(els.values())
        surv = sorted(f for f, v in els.items() if best - v <= 1e-6)
        assert ",".join(surv) == ex.answer


def test_balance_all_labels_every_level():
    from collections import Counter

    task = MisspecifiedModelConcentration()
    for level in (0, 2, 5):
        task.config.set_level(level)
        c = Counter()
        for _ in range(120):
            c[task.generate_example().answer] += 1
        assert len(c) >= 2, (level, dict(c))
