import random
import itertools
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'factorial_intervention_interactions (variant 2 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/factorial_intervention_interactions',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 525660630,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class InterventionConfig(Config):
    n_factors: int = 2
    levels: int = 3
    n_cells: int = 6

    def apply_difficulty(self, level):
        self.n_factors = 2 + (level >= 4)
        self.levels = 3 + (level >= 4)
        self.n_cells = min(14, 6 + level)


def _all_combos(n_factors, levels):
    return list(itertools.product(range(levels), repeat=n_factors))


def _balanced_design(n_factors, levels, rng, n_cells):
    full = _all_combos(n_factors, levels)
    top = (levels - 1,) * n_factors
    base = [top]
    rest = [c for c in full if c != top]
    k = n_cells - 1
    if k < 1:
        k = 1
    if len(rest) < k:
        k = len(rest)
    chosen = rng.sample(rest, k)
    for c in chosen:
        base.append(c)
    base.sort()
    return base


def _interaction_contrast(n_factors, levels, design, responses):
    if len(design) < 4:
        return None
    cell = dict(zip(design, responses))
    top = levels - 1
    n = float(len(design))
    grand_mean = sum(responses) / n

    def factor_mean(idx, val):
        s = 0.0
        c = 0
        for combo, r in zip(design, responses):
            if isinstance(idx, tuple):
                ok = all(combo[k] == v for k, v in zip(idx, val))
            else:
                ok = combo[idx] == val
            if ok:
                s += r
                c += 1
        if c == 0:
            return (None, 0)
        return (s / c, c)

    m00 = factor_mean(0, top)
    m01 = factor_mean(1, top)
    mjoint = factor_mean((0, 1), (top, top))
    if m00[1] < 1 or m01[1] < 1 or mjoint[1] < 1:
        return None

    e0 = m00[0] - grand_mean
    e1 = m01[0] - grand_mean
    additive = grand_mean + e0 + e1
    return int(round(mjoint[0] - additive))


class FactorialInterventionInteractions(Task):
    summary = "Separate joint intervention responses into baseline, individual, and higher-order interaction terms across binary or multivalued factors; return a requested pure two-way interaction contrast as an integer difference of observed responses."
    design_choice = "Factors are multivalued (e.g., 3 levels each) but the design is a balanced subset; the requested term is a two-way interaction contrast, and the answer is an integer difference of observed responses."
    config_cls = InterventionConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n_factors = cfg.n_factors
        levels = cfg.levels
        for _ in range(2000):
            design = _balanced_design(n_factors, levels, random, cfg.n_cells)
            responses = [random.randint(0, 30) for _ in design]
            int_val = _interaction_contrast(n_factors, levels, design, responses)
            if int_val is None:
                continue
            metadata = {
                "n_factors": n_factors,
                "levels": levels,
                "design": [list(c) for c in design],
                "responses": responses,
            }
            return Entry(metadata=metadata, answer=str(int_val))
        raise RuntimeError("failed to generate instance")

    def render_prompt(self, metadata):
        levels = metadata["levels"]
        factors = list(range(metadata["n_factors"]))
        design = metadata["design"]
        responses = metadata["responses"]

        lines = []
        lines.append("An experiment measures a response under joint interventions on factors labeled " +
                     ", ".join(f"F{k}" for k in factors) + ".")
        lines.append(f"Each factor takes integer levels 0..{levels - 1}. The design is a balanced subset; only these cells were measured:")
        for combo, r in zip(design, responses):
            tags = ", ".join(f"F{k}={v}" for k, v in zip(factors, combo))
            lines.append(f"  ({tags}): response {r}")
        lines.append("")
        lines.append("Compute the two-way interaction contrast for factors F0 and F1 at their top level, whose value is " + str(levels - 1) + ".")
        lines.append("Let G be the grand mean of all measured responses. Let E0 be (mean response over cells with F0 at its top level) minus G, and let E1 be (mean response over cells with F1 at its top level) minus G.")
        lines.append("The additive prediction at the (top, top) cell is G + E0 + E1.")
        lines.append("The interaction contrast is: (mean response over cells with both F0 and F1 at their top level) minus that additive prediction.")
        lines.append("")
        lines.append("Report the interaction contrast as a single integer, rounded to the nearest integer (half rounds away from zero).")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        ans = parse_int(answer)
        if ans is None:
            return 0.0
        return 1.0 if ans == int(entry.answer) else 0.0


def parse_int(answer):
    if isinstance(answer, int):
        return answer
    if isinstance(answer, float):
        return int(answer)
    if isinstance(answer, str):
        s = answer.strip()
        if s in ("", "-", "+"):
            return None
        try:
            return int(round(float(s)))
        except (ValueError, TypeError):
            return None
    return None
