import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _bounds(cells, mode):
    n000, n001, n010, n011, n100, n101, n110, n111 = cells
    N = sum(cells)
    n0 = n000 + n001 + n010 + n011
    n1 = n100 + n101 + n110 + n111
    px1 = (n010 + n011 + n110 + n111) / N
    px0 = (n000 + n001 + n100 + n101) / N
    py1x1 = (n011 + n111) / N
    py1x0 = (n001 + n101) / N
    ey_x1 = (n011 + n111) / (n010 + n011 + n110 + n111)
    ey_x0 = (n001 + n101) / (n000 + n001 + n100 + n101)
    if mode == "none":
        low = py1x1 - (py1x0 + px1)
        high = (py1x1 + px0) - py1x0
    elif mode == "monotone":
        low = 0.0
        high = ey_x1 - ey_x0
    else:
        ez0 = (n010 + n011) / n0
        ez1 = (n110 + n111) / n1
        oy0 = (n001 + n011) / n0
        oy1 = (n101 + n111) / n1
        denom = ez1 - ez0
        if abs(denom) < 1e-9:
            return (None, None)
        wald = (oy1 - oy0) / denom
        low = high = wald
    low = max(-1.0, min(1.0, low))
    high = max(-1.0, min(1.0, high))
    if low > high + 1e-9:
        return (None, None)
    return (low, high)


@dataclass
class PartialIdentificationConfig(Config):
    level: int = 0
    precision: int = 2

    def apply_difficulty(self, level):
        self.level = level
        self.precision = 2

    def set_level(self, level):
        self.apply_difficulty(level)


class PartialIdentificationBounds(Task):
    summary = "From observational 2x2x2 contingency tables bracket a causal effect under none (Manski), monotone response, or instrument (Wald) assumptions by extremizing stratum terms per formula and answer the bound interval endpoints."

    design_choice = "Use a fixed 2x2x2 table structure with binary exposure, outcome, and instrument, varying only the cell counts to shift bound tightness."

    config_cls = PartialIdentificationConfig

    def _bounds(self, cells, mode):
        n000, n001, n010, n011, n100, n101, n110, n111 = cells
        N = sum(cells)
        n0 = n000 + n001 + n010 + n011
        n1 = n100 + n101 + n110 + n111
        px1 = (n010 + n011 + n110 + n111) / N
        px0 = (n000 + n001 + n100 + n101) / N
        py1x1 = (n011 + n111) / N
        py1x0 = (n001 + n101) / N
        ey_x1 = (n011 + n111) / (n010 + n011 + n110 + n111)
        ey_x0 = (n001 + n101) / (n000 + n001 + n100 + n101)
        if mode == "none":
            low = py1x1 - (py1x0 + px1)
            high = (py1x1 + px0) - py1x0
        elif mode == "monotone":
            low = 0.0
            high = ey_x1 - ey_x0
        else:
            ez0 = (n010 + n011) / n0
            ez1 = (n110 + n111) / n1
            oy0 = (n001 + n011) / n0
            oy1 = (n101 + n111) / n1
            wald = (oy1 - oy0) / (ez1 - ez0)
            low = high = wald
        low = max(-1.0, min(1.0, low))
        high = max(-1.0, min(1.0, high))
        if low > high + 1e-9:
            return (None, None)
        return (low, high)

    def generate_entry(self):
        base = 150 + self.config.level * 140
        while True:
            mode = random.choice(["none", "monotone", "instrument"])
            cells = self._draw_cells(mode, base)
            lower, upper = _bounds(cells, mode)
            if lower is None or upper is None:
                continue
            prec = self.config.precision
            low = round(lower, prec)
            high = round(upper, prec)
            if abs(low) < 10 ** (-prec):
                low = 0.0
            if abs(high) < 10 ** (-prec):
                high = 0.0
            if low > high:
                low, high = high, low
            json_cells = [int(c) for c in cells]
            return Entry(metadata={
                "cells": json_cells,
                "mode": mode,
                "precision": prec,
            }, answer=f"{low:.{prec}f},{high:.{prec}f}")

    def _draw_cells(self, mode, base):
        lo = max(30, base // 4)
        hi = max(31, base // 3)
        if mode != "instrument":
            return [random.randrange(max(30, base // 6), max(31, base // 3))
                    for _ in range(8)]
        n0 = random.randrange(base, max(base + 1, int(base * 1.3)))
        n1 = random.randrange(base, max(base + 1, int(base * 1.3)))
        ex0 = random.uniform(0.2, 0.5)
        ex1 = ex0 + random.uniform(0.15, 0.4)
        ex1 = min(ex1, 0.85)
        oy0 = random.uniform(0.2, 0.7)
        delta = random.uniform(-0.4, 0.4)
        ey0 = min(0.85, max(0.15, oy0 + delta))
        ey1 = min(0.85, max(0.15, oy0 + delta + random.uniform(-0.3, 0.3)))
        def xcounts(n, ex):
            nx = int(round(n * ex))
            return nx, n - nx
        def ysplit_by(x0, x1, eyx0, eyx1):
            return [int(round(x0 * (1 - eyx0))), int(round(x0 * eyx0)),
                    int(round(x1 * (1 - eyx1))), int(round(x1 * eyx1))]
        n000, n001, n010, n011 = ysplit_by(*xcounts(n0, ex0), ey0, ey0 + random.uniform(-0.3, 0.3))
        n100, n101, n110, n111 = ysplit_by(*xcounts(n1, ex1), ey1, ey1 + random.uniform(-0.3, 0.3))
        return [n000, n001, n010, n011, n100, n101, n110, n111]

    def render_prompt(self, metadata):
        cells = metadata["cells"]
        mode = metadata["mode"]
        prec = metadata["precision"]
        n000, n001, n010, n011, n100, n101, n110, n111 = cells
        if mode == "none":
            assum = ("an unidentified causal relation between a binary exposure X and a binary "
                     "outcome Y, with no further assumption, giving the sharp Manski (natural) bound")
        elif mode == "monotone":
            assum = ("monotone response, meaning the outcome Y under exposure 1 is never below its "
                     "value under exposure 0, giving the sharp monotone-response bound")
        else:
            assum = ("a binary instrument Z satisfying the exclusion restriction and monotone response, "
                     "giving the sharp Wald (compliance) bound")
        return (
            f"A cohort is cross-classified by binary instrument Z (0/1), binary exposure X (0/1), and "
            f"binary outcome Y (0/1). The observed counts are:\n"
            f"Z=0, X=0: Y=0 has {n000}, Y=1 has {n001}\n"
            f"Z=0, X=1: Y=0 has {n010}, Y=1 has {n011}\n"
            f"Z=1, X=0: Y=0 has {n100}, Y=1 has {n101}\n"
            f"Z=1, X=1: Y=0 has {n110}, Y=1 has {n111}\n"
            f"Under {assum}, compute the identified set for the average causal effect of X on Y, "
            f"the probability difference E[Y(1)]-E[Y(0)]. Report the lower and upper endpoints of that "
            f"interval, each rounded to {prec} decimals, as `L,U` (e.g. `0.25,0.75`)."
        )

    def render_payload(self, payload):
        return self.render_prompt(payload)

    def score_answer(self, answer, entry):
        try:
            low_s, high_s = answer.strip().split(",")
            low_v = float(low_s)
            high_v = float(high_s)
        except Exception:
            return 0.0
        mode = entry["metadata"]["mode"]
        prec = entry["metadata"]["precision"]
        cells = entry["metadata"]["cells"]
        gold_low, gold_high = _bounds(cells, mode)
        gold_low = round(gold_low, prec)
        gold_high = round(gold_high, prec)
        tol = 10 ** (-prec)
        if abs(low_v - gold_low) <= tol and abs(high_v - gold_high) <= tol:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'partial_identification_bounds (variant 2 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/partial_identification_bounds',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1211525277,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
