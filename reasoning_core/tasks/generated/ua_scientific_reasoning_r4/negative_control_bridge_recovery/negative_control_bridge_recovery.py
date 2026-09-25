"""Negative-control bridge recovery for a causal mean under latent confounding.

A real-valued outcome Y is treated by a binary treatment A with an unmeasured
categorical confounder U that also drives two negative-control proxies: an exposure
proxy Z (distribution depends only on U; no direct effect on Y) and an outcome proxy W
(depends on U and A). For a queried treatment arm the causal mean E[Y(a)] is recovered
through the outcome bridge h on Z, which is identified exactly when the observable
design matrix K = [P(Z | A=a, W)] has full column rank (completeness of the exposure
proxy). We vary the sizes of the categorical supports and the number of proxy levels
(proxy redundancy), and report the identified causal mean or nonidentifiability.
"""

import random
from dataclasses import dataclass

import numpy as np

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'negative_control_bridge_recovery (variant 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/negative_control_bridge_recovery',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class NegativeControlBridgeConfig(Config):
    ku: int = 2
    kz: int = 2
    p_nonident: float = 0.22

    def apply_difficulty(self, level):
        self.ku = 2 + (1 if level >= 3 else 0) + (1 if level >= 6 else 0)
        self.kz = self.ku
        self.p_nonident = 0.22


def _prop(size):
    """A random probability vector of the given length (module RNG only)."""
    raw = [random.uniform(0.03, 1.0) for _ in range(size)]
    s = sum(raw)
    return [x / s for x in raw]


def _observed(ku, kz, arm, under, degenerate):
    """Draw one structural instance; return (kw, K_rows, ey, pz, structural, kind).

    ``degenerate`` signals the non-identifiable case where the exposure proxy carries no
    information about U, collapsing the design matrix to rank 1. When ``under`` is set and
    not degenerate, kw is drawn below kz so the design matrix is under-determined.
    """
    p_u = _prop(ku)
    pi = [random.uniform(0.2, 0.8) for _ in range(ku)]  # P(A=1 | U=u)
    pa_u = [pi[u] if arm == 1 else 1.0 - pi[u] for u in range(ku)]
    # Z levels: z_prior[u][z] = P(Z=z | U=u), a probability vector over z per u.
    if degenerate:
        flat = _prop(kz)
        z_prior = [list(flat) for _ in range(ku)]
    else:
        z_prior = [_prop(kz) for _ in range(ku)]
    # W support size: under-determined (kw < kz) or redundant (kw in {kz, kz+1}).
    if under and not degenerate:
        kw = kz - 1
        if kw < 1:
            kw = 1
    else:
        kw = random.choice([kz, kz + 1])
    # W levels: w_prior[u][w] = P(W=w | A=arm, U=u), probability over w per u.
    w_prior = [_prop(kw) for _ in range(ku)]
    m = [random.uniform(-5.0, 5.0) for _ in range(ku)]  # E[Y | U=u, A=arm]

    def coef(u, w):
        return w_prior[u][w] * pa_u[u] * p_u[u]

    den = [sum(coef(u, w) for u in range(ku)) for w in range(kw)]

    def k_val(z, w):
        return sum(z_prior[u][z] * w_prior[u][w] * pa_u[u] * p_u[u] for u in range(ku)) / den[w]

    def ey_val(w):
        return sum(m[u] * w_prior[u][w] * pa_u[u] * p_u[u] for u in range(ku)) / den[w]

    PZ = [sum(z_prior[u][z] * p_u[u] for u in range(ku)) for z in range(kz)]
    structural = sum(m[u] * p_u[u] for u in range(ku))
    K_rows = [[round(k_val(z, w), 4) for z in range(kz)] for w in range(kw)]
    ey = [round(ey_val(w), 4) for w in range(kw)]
    pz = [round(v, 4) for v in PZ]
    return kw, K_rows, ey, pz, structural


def _rank(K_rows):
    return int(np.linalg.matrix_rank(np.array(K_rows, dtype=float)))


def _score(answer, gold):
    if not isinstance(answer, str):
        return 0.0
    a = answer.strip()
    if gold == "nonidentifiable":
        return 1.0 if a == "nonidentifiable" else 0.0
    if a == "nonidentifiable":
        return 0.0
    try:
        x = float(a)
    except ValueError:
        return 0.0
    return 1.0 if abs(x - float(gold)) <= 0.5e-2 else 0.0


class NegativeControlBridgeRecovery(Task):
    summary = ("Use paired negative-control measurements to recover an outcome bridge "
               "despite latent confounding; vary categorical supports and proxy "
               "redundancy; return the identified causal mean or nonidentifiability.")
    design_choice = ("Vary the support size of the categorical confounder and proxy "
                     "variables across instances, forcing solvers to check identifiability "
                     "via rank conditions before reporting the mean.")
    config_cls = NegativeControlBridgeConfig
    task_version = 2

    def generate_entry(self):
        ku = self.config.ku
        kz = self.config.kz
        arm = random.choice([0, 1])
        under = random.random() < self.config.p_nonident
        degenerate = under and (kz > 1) and (random.random() < 0.5)
        for _ in range(400):
            kw, K_rows, ey, pz, structural = _observed(ku, kz, arm, under, degenerate)
            rank = _rank(K_rows)
            if under:
                # nonidentifiable: rank condition must fail (either kw<kz or degenerate)
                if rank < kz:
                    gold = "nonidentifiable"
                    break
            else:
                if rank == kz:
                    sol = np.linalg.lstsq(
                        np.array(K_rows, dtype=float), np.array(ey, dtype=float), rcond=None
                    )[0]
                    theta = float(np.dot(sol, pz))
                    if -5.01 <= theta <= 5.01 and abs(theta - structural) < 0.05:
                        gold = f"{theta:.3f}"
                        break
        else:
            raise RuntimeError("NegativeControlBridgeRecovery: no admissible instance")
        metadata = {
            "arm": arm,
            "ku": ku,
            "kz": kz,
            "kw": kw,
            "identifiable": not under,
            "K_rows": K_rows,
            "ey": ey,
            "pz": pz,
            "structural_mean": float(structural),
        }
        return Entry(metadata=metadata, answer=gold)

    def render_prompt(self, metadata):
        arm = metadata["arm"]
        kz = metadata["kz"]
        kw = metadata["kw"]
        pz = ", ".join(f"{v:.4f}" for v in metadata["pz"])
        ey = ", ".join(f"{v:.4f}" for v in metadata["ey"])
        klines = "\n".join(
            "   [" + ", ".join(f"{v:.4f}" for v in row) + "]" for row in metadata["K_rows"]
        )
        return (
            f"In an observational study a real-valued outcome Y is treated by a binary "
            f"treatment A in {{0,1}}. An unmeasured categorical confounder U confounds A "
            f"and Y. Two negative-control proxies are observed: an exposure proxy Z whose "
            f"distribution depends only on U (so Z has no direct effect on Y), and an "
            f"outcome proxy W whose distribution depends on U and A. Z has {kz} levels "
            f"(z_0..z_{{{kz - 1}}}) and W has {kw} levels (w_0..w_{{{kw - 1}}}).\n"
            f"For the queried treatment arm a={arm}, the causal mean E[Y(a)] is recovered "
            f"through the outcome bridge h on Z, E[Y(a)] = sum_z h(z)*P(Z=z), where h "
            f"solves, for every W level w, sum_z h(z)*P(Z=z|A=a,W=w) = E[Y|A=a,W=w]. This "
            f"is identified exactly when the kw x kz design matrix K=[P(Z=z|A=a,W=w)] has "
            f"full column rank {kz}; if so compute the bridge and the mean, otherwise "
            f"E[Y(a)] is nonidentifiable.\n"
            f"Marginal distribution of Z over the population, P(Z=z):\n"
            f"   {pz}\n"
            f"For arm a={arm}:\n"
            f"   E[Y|A={arm},W=w] = [ {ey} ]\n"
            f"   P(Z=z|A={arm},W=w), rows w_0..w_{{{kw - 1}}}, columns z_0..z_{{{kz - 1}}}:\n"
            f"{klines}\n"
            f"Report E[Y({arm})] to three decimals, or the single word 'nonidentifiable' "
            f"if the full-column-rank condition fails."
        )

    def score_answer(self, answer, entry):
        return _score(answer, entry.answer)
