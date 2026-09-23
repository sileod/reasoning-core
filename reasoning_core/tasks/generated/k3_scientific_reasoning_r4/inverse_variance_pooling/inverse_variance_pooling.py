"""Inverse-variance pooling of study effect estimates.

Pool per-study effect estimates by inverse-variance weights, compute Cochran's
Q and the I^2 heterogeneity index, then judge heterogeneity against a
significance threshold; when triggered, fall back to a random-effects model
(with a DerSimonian-Laird between-study variance, tau^2) and answer the pooled
mean and verdict accordingly.
"""

import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'inverse_variance_pooling (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/inverse_variance_pooling',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class InverseVariancePoolingConfig(Config):
    n_studies: int = 4
    tau2_level: float = 0.15
    alpha: int = 10  # tail area in percent, e.g. 10 => chi^(2) threshold at 90th pct

    def apply_difficulty(self, level):
        n = 2 + 2 * level
        if n > 8:
            n = 8
        self.n_studies = n
        self.tau2_level = {0: 0.0, 1: 0.03, 2: 0.08, 3: 0.15, 4: 0.25, 5: 0.4, 6: 0.6}[min(level, 6)]
        self.alpha = 10


def _qf(alpha, df):
    """Percent point of chi-squared at the (1 - alpha/100) quantile (scipy)."""
    from scipy.stats import chi2
    return float(chi2.ppf(1.0 - alpha / 100.0, df))


def _pvalue(q, df):
    from scipy.stats import chi2
    return float(chi2.sf(q, df))


def _fmt(x):
    return f"{x:.3f}"


def _compute(estimates, variances, alpha):
    """Return (pooled_mean, q, i2, verdict_label)."""
    k = len(estimates)
    weights = [1.0 / v for v in variances]
    denom = sum(weights)
    pool_fe = sum(w * e for w, e in zip(weights, estimates)) / denom
    q = sum(w * (e - pool_fe) ** 2 for w, e in zip(weights, estimates))
    df = k - 1
    i2 = (q - df) / q * 100.0 if q > 0 else 0.0
    i2 = max(i2, 0.0)
    crit = _qf(alpha, df)
    p = _pvalue(q, df)
    if q <= crit or p > alpha / 100.0:
        verdict = "fixed"
        pooled = pool_fe
    else:
        verdict = "random"
        # DerSimonian-Laird tau^2
        wsum = denom
        w2 = sum(w * w for w in weights)
        q2 = max(q - df, 0.0)
        tau2 = q2 / (wsum - w2 / wsum) if (wsum - w2 / wsum) > 0 else 0.0
        rweights = [1.0 / (v + tau2) for v in variances]
        pooled = sum(w * e for w, e in zip(rweights, estimates)) / sum(rweights)
    return pooled, q, i2, verdict


def score_answer(answer, entry):
    if not isinstance(answer, str):
        return 0.0
    parts = answer.split(";")
    if len(parts) != 4:
        return 0.0
    try:
        m = float(parts[0])
        q = float(parts[1])
        i2 = float(parts[2])
        verdict = parts[3].strip()
    except ValueError:
        return 0.0
    gold = entry.answer.split(";")
    gm = float(gold[0])
    gq = float(gold[1])
    gi2 = float(gold[2])
    gver = gold[3].strip()
    if verdict != gver:
        return 0.0
    if abs(m - gm) > 1e-2:
        return 0.0
    if abs(q - gq) > 1e-1:
        return 0.0
    if abs(i2 - gi2) > 0.5:
        return 0.0
    return 1.0


class InverseVariancePooling(Task):
    summary = ("Pool effect estimates by inverse-variance weights across study sets: form the "
               "pooled mean, Q and I2, judge heterogeneity, switch to random effects when "
               "triggered; answer pooled values and verdict.")
    design_choice = ("Answer format: a canonical 4-tuple string of pooled mean, Q statistic, I2 "
                     "percentage, and verdict label (fixed/random)")
    config_cls = InverseVariancePoolingConfig
    task_version = 2

    def generate_entry(self):
        k = self.config.n_studies
        alpha = self.config.alpha
        tau2 = self.config.tau2_level
        base = random.uniform(-3.0, 3.0)
        # within-study standard errors in a broad range
        while True:
            ses = []
            for _ in range(k):
                ses.append(random.uniform(0.4, 2.5))
            estimates = [base + random.gauss(0, tau2) + random.gauss(0, s) for s in ses]
            variances = [s * s for s in ses]
            pool_fe, q, i2, verdict = _compute(estimates, variances, alpha)
            # sanity: pooled mean must be a finite real number
            if math.isfinite(pool_fe) and 0.0 <= i2 <= 100.0:
                break
        answer = f"{_fmt(pool_fe)};{_fmt(q)};{_fmt(i2)};{verdict}"
        metadata = {
            "estimates": [float(e) for e in estimates],
            "variances": [float(v) for v in variances],
            "n_studies": k,
            "alpha_pct": alpha,
            "tau2": float(tau2),
            "pooled_mean": float(pool_fe),
            "q": float(q),
            "i2": float(i2),
            "verdict": verdict,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        for i, (e, v) in enumerate(zip(metadata["estimates"], metadata["variances"]), 1):
            lines.append(f"Study {i}: effect {e:.3f}, variance {v:.3f}")
        body = "\n".join(lines)
        return (
            f"Five-study meta-analysis is impossible here; use a study set. For the "
            f"studies below, perform an inverse-variance pooling (fixed-effect) of effect "
            f"estimates with weights 1/variance. Compute Cochran's Q = sum(w_i*(e_i - pooled)^2) "
            f"and the heterogeneity I2 = max(0, (Q - (k-1))/Q)*100 percent, then test "
            f"heterogeneity at the {metadata['alpha_pct']}% two-tailed level against "
            f"chi-squared(k-1): if Q exceeds the critical value, switch to a random-effects "
            f"model using DerSimonian-Laird tau^2 and re-pool. Report the pooled mean (3 "
            f"decimals), the Q statistic (3 decimals), the I2 percentage (3 decimals), and the "
            f"verdict label 'fixed' or 'random', as a semicolon-separated 4-tuple: "
            f"<mean>;<Q>;<I2>;<verdict>.\n\n"
            f"{body}"
        )

    def score_answer(self, answer, entry):
        return score_answer(answer, entry)
