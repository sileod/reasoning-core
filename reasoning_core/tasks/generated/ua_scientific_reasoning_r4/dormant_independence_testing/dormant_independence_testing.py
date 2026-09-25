import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


def _fr(fr):
    return f"{fr.numerator}/{fr.denominator}"


def _compute(cells, xout):
    nx = len(cells)
    nm = len(cells[0])
    N = sum(sum(row) for plane in cells for row in plane)
    cx = [sum(sum(r) for r in plane) for plane in cells]
    cxm = [[sum(r) for r in plane] for plane in cells]
    px = [Fraction(c, N) for c in cx]

    out = []
    for xi in range(nx):
        naive = Fraction(sum(cells[xi][m][xout] for m in range(nm)), cx[xi])
        dormant = Fraction(0, 1)
        for m in range(nm):
            pmx = Fraction(cxm[xi][m], cx[xi])
            inner = Fraction(0, 1)
            for x2 in range(nx):
                inner += Fraction(cells[x2][m][xout], cxm[x2][m]) * px[x2]
            dormant += pmx * inner
        out.append((naive, dormant))
    return out


def _gold(cells, xout):
    res = _compute(cells, xout)
    gaps = [abs(n - d) for n, d in res]
    xi = max(range(len(gaps)), key=lambda i: gaps[i])
    naive, dormant = res[xi]
    return f"{_fr(naive)} != {_fr(dormant)}"


@dataclass
class DormantIDConfig(Config):
    level: int = 0
    m_states: int = 2
    latent_states: int = 2
    n_units: int = 320

    def apply_difficulty(self, level):
        self.level = level
        self.m_states = 2 + level // 2
        self.latent_states = 2 + (level // 3)
        self.n_units = 320 + level * 40


def _probsample(probs):
    r = random.random()
    acc = 0.0
    for i, p in enumerate(probs):
        acc += p
        if r <= acc:
            return i
    return len(probs) - 1


class DormantIndependenceTesting(Task):
    summary = ("Latent-variable causal kernels: a binary exposure acts on a binary outcome only through "
               "a mediator while a hidden confounder corrupts observable-independence checks; by "
               "reweighting and marginalizing the causal kernel, detect the violated polynomial equality "
               "between the naive conditional probability and the front-door reweighted causal probability, "
               "stated as a symbolic fraction of counts.")

    design_choice = "Instances present a causal kernel with hidden nodes; the solver must output the minimal polynomial equality among observable joint probabilities that is violated, expressed as a symbolic fraction of counts."

    config_cls = DormantIDConfig

    def generate_entry(self):
        while True:
            cells = self._draw()
            res = _compute(cells, 1)
            if all(n == d for n, d in res):
                continue
            ans = _gold(cells, 1)
            return Entry(metadata={
                "cells": cells,
                "xout": 1,
                "answer": ans,
            }, answer=ans)

    def _draw(self):
        K = self.config.latent_states
        nx = 2
        nm = self.config.m_states
        ny = 2
        N = self.config.n_units

        while True:
            th = [random.uniform(0.2, 1.0) for _ in range(K)]
            p_h = [t / sum(th) for t in th]
            p_x1h = [random.uniform(0.1, 0.9) for _ in range(K)]
            p_mx = [[random.uniform(0.1, 0.9) for _ in range(nx)] for _ in range(nm)]
            p_y1xh = [[random.uniform(0.05, 0.95) for _ in range(K)] for _ in range(nx)]

            cells = [[[0 for _ in range(ny)] for _ in range(nm)] for _ in range(nx)]
            for _ in range(N):
                h = _probsample(p_h)
                x = _probsample([1 - p_x1h[h], p_x1h[h]])
                mprobs = [1.0 / nm for _ in range(nm)]
                mprobs = [p_mx[m][x] / sum(p_mx[t][x] for t in range(nm)) for m in range(nm)]
                m = _probsample(mprobs)
                y = _probsample([1 - p_y1xh[x][h], p_y1xh[x][h]])
                cells[x][m][y] += 1

            if all(cells[x][m][y] > 0 for x in range(nx) for m in range(nm) for y in range(ny)):
                return cells

    def render_prompt(self, metadata):
        cells = metadata["cells"]
        xout = metadata["xout"]
        nx = len(cells)
        nm = len(cells[0])
        lines = [
            "A binary exposure X acts on a binary outcome Y only through a mediator M (X -> M -> Y), "
            "but a hidden confounder makes the raw observational link between X and Y misleading. "
            "The cohort counts by (X, M, Y) are:"]
        for x in range(nx):
            for m in range(nm):
                row = "  ".join(f"Y={y}: {cells[x][m][y]}" for y in range(len(cells[0][0])))
                lines.append(f"  X={x} M={m} -> {row}")
        lines.append(
            "Name the standard algorithm: apply the front-door adjustment to estimate the causal "
            f"probability P(Y={xout} | do(X)) by marginalizing over the kernel, and compare it with the "
            f"naive conditional probability P(Y={xout} | X) that an ordinary conditional-independence "
            "shortcut would read off. Give the violated polynomial equality -- the reduced-fraction "
            "forms of the two values, separated by ` != ` -- for the X level where they diverge most; "
            "write it as e.g. `2/5 != 3/7`. If you cannot give a well-defined reduced fraction on each "
            "side, do not guess.")
        return "\n".join(lines)

    def render_payload(self, payload):
        return self.render_prompt(payload)

    def score_answer(self, answer, entry):
        try:
            left, right = answer.split("!=")
            ln, ld = left.strip().split("/")
            rn, rd = right.strip().split("/")
            fracs = (Fraction(int(ln), int(ld)), Fraction(int(rn), int(rd)))
        except Exception:
            return 0.0
        cells = entry["metadata"]["cells"]
        xout = entry["metadata"]["xout"]
        res = _compute(cells, xout)
        target = tuple(fracs)
        for naive, dormant in res:
            if target == (naive, dormant) or target == (dormant, naive):
                return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'dormant_independence_testing (variant 2 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scientific_reasoning_r4/dormant_independence_testing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1705404348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
