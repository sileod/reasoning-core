"""Asymptotic posterior concentration under misspecification.

Instances give a data-generating law g over a finite grid, rival predictive
models (parametric families differing in functional form: geometric, Poisson,
and a rising/reverse-geometric family), and prior masses. The true law is kept
outside every candidate family. For each family we form its maximized expected
log likelihood ELBO_m = max_theta E_g[log p_theta(X)] (the per-datum expected
log evidence). Asymptotically the posterior concentrates on the family or
families whose ELBO is maximal; the answer is the sorted subset of those
survivors, ties listed explicitly. Prior masses are stated but do not alter
which families survive in the limit.
"""

import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'misspecified_model_concentration (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/misspecified_model_concentration',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

FAMILIES = ("Geometric", "Poisson", "Rising")


def _geo_elbo(mean_idx):
    """Maximized expected log likelihood of the geometric family (1-a) a^i."""
    if mean_idx <= 0:
        # degenerate limit: all mass on slot 0, geometric has a point mass-like fit
        return 0.0
    a = mean_idx / (1.0 + mean_idx)
    return math.log(1.0 - a) + mean_idx * math.log(a)


def _poisson_elbo(mean_idx, g):
    """Maximized expected log likelihood of the Poisson family lam^i e^-lam / i!."""
    lam = mean_idx
    if lam < 1e-12:
        el = sum(gi * -_logfact(i) for i, gi in enumerate(g))
        return el
    return mean_idx * math.log(lam) - lam - sum(gi * _logfact(i) for i, gi in enumerate(g))


def _logfact(n):
    return math.lgamma(n + 1.0)


def _rising_elbo(g, mean_idx):
    """Maximized expected log likelihood of the rising family p(i) prop a^(K-1-i)."""
    k = len(g)
    jbar = (k - 1) - mean_idx  # mean distance-from-top coordinate

    def neg_elbo(loga):
        a = math.exp(max(-30.0, min(loga, -1e-9)))
        Z = sum(a ** j for j in range(k))
        el = jbar * math.log(a) - math.log(Z)
        return -el

    from scipy.optimize import minimize_scalar
    res = minimize_scalar(neg_elbo, bounds=(-25.0, -1e-8), method="bounded")
    return -res.fun


def _expected_log_likelihood(family, g, mean_idx):
    if family == "Geometric":
        val = _geo_elbo(mean_idx)
    elif family == "Poisson":
        val = _poisson_elbo(mean_idx, g)
    elif family == "Rising":
        val = _rising_elbo(g, mean_idx)
    else:  # pragma: no cover
        raise ValueError(family)
    return float(val)


def score_answer(answer, entry):
    if not isinstance(answer, str):
        return 0.0
    gold = entry.answer
    tokens = [t.strip() for t in answer.split(",") if t.strip()]
    for t in tokens:
        if t not in FAMILIES:
            return 0.0
    if not tokens:
        return 0.0
    if len(tokens) != len(set(tokens)):
        return 0.0
    if tokens == sorted(tokens) and ",".join(tokens) == gold:
        return 1.0
    return 0.0


@dataclass
class MisspecifiedModelConfig(Config):
    k: int = 4
    noise: float = 0.3

    def apply_difficulty(self, level):
        self.k = 4 + level
        self.noise = 0.25 + 0.1 * level


def _prototype(target, k):
    """A best-fitting distribution of the given family (before added noise)."""
    if target == "Geometric":
        a = random.uniform(0.05, 0.7)
        raw = [(1 - a) * a ** i for i in range(k)]
    elif target == "Poisson":
        lam = random.uniform(0.3, max(0.6, k / 2.0))
        raw = [math.exp(-lam) * lam ** i / math.factorial(i) for i in range(k)]
    else:  # Rising
        a = random.uniform(0.1, 0.7)
        raw = [a ** (k - 1 - i) for i in range(k)]
    s = sum(raw)
    return [v / s for v in raw]


def _draw_weights(k, target, noise):
    p = _prototype(target, k)
    base = [v * math.exp(random.gauss(0.0, noise)) for v in p]
    s = sum(base)
    return [v / s for v in base]


class MisspecifiedModelConcentration(Task):
    summary = ("Given a data-generating law, rival parametric families of different "
               "functional form (geometric, Poisson, rising) and prior masses, "
               "compute each family's maximized expected log likelihood; return the "
               "sorted subset of families tied for the maximum (survivors).")
    design_choice = ("Instances specify rival models as parametric families differing "
                     "in functional form, with true law outside all families; answer is "
                     "the subset of models whose expected log likelihood is maximal, with "
                     "ties listed explicitly.")
    config_cls = MisspecifiedModelConfig
    task_version = 2

    def generate_entry(self):
        k = self.config.k
        noise = self.config.noise
        while True:
            target = random.choice(list(FAMILIES))
            g = _draw_weights(k, target, noise)
            if not all(math.isfinite(gi) and gi > 1e-9 for gi in g):
                continue
            s = sum(g)
            if not (0.999 < s < 1.001):
                continue
            mean_idx = sum(i * gi for i, gi in enumerate(g))
            els = {f: _expected_log_likelihood(f, g, mean_idx) for f in FAMILIES}
            if not all(math.isfinite(v) for v in els.values()):
                continue
            best = max(els.values())
            tol = 1e-7
            survivors = tuple(sorted(f for f, v in els.items() if best - v <= tol))
            if not survivors:
                continue
            # the intended family must actually survive (truth is a perturbed member
            # of its own family); reject draws where the noise flipped the winner
            if target not in survivors:
                continue
            break
        w = sorted(random.uniform(0.1, 1.0) for _ in range(3))
        wsum = sum(w)
        priors = [wi / wsum for wi in w]
        answer = ",".join(survivors)
        metadata = {
            "g": [float(gi) for gi in g],
            "k": k,
            "target": target,
            "families": list(FAMILIES),
            "priors": [float(p) for p in priors],
            "elbo": {f: float(v) for f, v in els.items()},
            "survivors": list(survivors),
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        g = metadata["g"]
        gline = ", ".join(f"{gi:.4f}" for gi in g)
        priors = metadata["priors"]
        pline = ", ".join(f"{p:.3f}" for p in priors)
        idx = list(range(len(g)))
        gridline = ", ".join(str(i) for i in idx)
        return (
            "We observe data drawn from a true law g over the support "
            "({" + gridline + "}) with probabilities (" + gline + "). "
            "The true law lies outside all candidate families below. Rival predictive "
            "models are the following parametric families over that support "
            "(each fitted freely within its family; prior masses are "
            "(" + pline + ") and do not affect which families win asymptotically):\n"
            "- Geometric: p(i) = (1-a) a^i, 0<a<1.\n"
            "- Poisson: p(i) = lam^i e^(-lam) / i!, lam>0, with 0!:=1.\n"
            "- Rising: p(i) proportional to a^(K-1-i), 0<a<1.\n"
            "For each family compute its maximized expected log likelihood "
            "ELBO = max over its parameter of E_g[log p(X)] (the per-datum expected log "
            "evidence). Asymptotically the posterior concentrates on the family or "
            "families whose ELBO is maximal (K-L projection closest to g). Report the "
            "families tied for the maximum as a comma-separated list sorted "
            "alphabetically; a single surviving family is reported alone, e.g. "
            "\"Poisson\"; a tie of two is \"Geometric,Poisson\"."
        )

    def score_answer(self, answer, entry):
        return score_answer(answer, entry)
