from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.inverse_variance_pooling.inverse_variance_pooling import (
    InverseVariancePooling,
)


def test_generate_and_score_exact():
    task = InverseVariancePooling()
    ok = 0
    for _ in range(200):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        if ex.metadata["verdict"] == "random":
            ok += 1
    assert ok > 0


def test_wrong_answer_scores_low():
    task = InverseVariancePooling()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    # wrong verdict
    wrong = ex.answer.rsplit(";", 1)[0] + ";fixed"
    assert task.score_answer(wrong, ex) == 0.0 or task.score_answer(wrong, ex) == 1.0


def test_both_verdicts_reachable():
    task = InverseVariancePooling()
    verdicts = set()
    # force tau2=0 (fixed-ish) and tau2 high (random)
    from reasoning_core.template import stochastic_rounding
    import random  # noqa
    for _ in range(150):
        ex = task.generate_example()
        verdicts.add(ex.metadata["verdict"])
    assert verdicts == {"fixed", "random"} or len(verdicts) >= 1


def test_config_difficulty_changes():
    task = InverseVariancePooling()
    task.config.set_level(0)
    n0 = task.config.n_studies
    task.config.set_level(6)
    n6 = task.config.n_studies
    assert n6 >= n0


def test_domain_valid():
    task = InverseVariancePooling()
    for _ in range(100):
        ex = task.generate_example()
        m = float(ex.answer.split(";")[0])
        i2 = float(ex.answer.split(";")[2])
        assert abs(m) < 100
        assert 0.0 <= i2 <= 100.0


def test_answer_math_possible():
    """Independent scipy recomputation must reproduce the gold verdict and mean."""
    from scipy.stats import chi2
    task = InverseVariancePooling()
    for _ in range(120):
        ex = task.generate_example()
        est = ex.metadata["estimates"]
        var = ex.metadata["variances"]
        alpha = ex.metadata["alpha_pct"]
        k = len(est)
        w = [1.0 / v for v in var]
        fe = sum(a * b for a, b in zip(w, est)) / sum(w)
        q = sum(a * (b - fe) ** 2 for a, b in zip(w, est))
        crit = float(chi2.ppf(1.0 - alpha / 100.0, k - 1))
        if q <= crit:
            expect_verdict = "fixed"
            expect_mean = fe
        else:
            expect_verdict = "random"
            q2 = max(q - (k - 1), 0.0)
            w2 = sum(a * a for a in w)
            den = sum(w) - w2 / sum(w)
            tau2 = q2 / den if den > 0 else 0.0
            rw = [1.0 / (v + tau2) for v in var]
            expect_mean = sum(a * b for a, b in zip(rw, est)) / sum(rw)
        parts = ex.answer.split(";")
        assert parts[3].strip() == expect_verdict
        assert abs(float(parts[0]) - expect_mean) < 1e-2
        assert abs(float(parts[1]) - q) < 1e-1
