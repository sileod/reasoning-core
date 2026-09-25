import random
from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'projective_configuration_invariants (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_invariants_r4/projective_configuration_invariants',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _cr_frac(vals):
    v0, v1, v2, v3 = (Fraction(v, 1) for v in vals)
    return ((v0 - v2) * (v1 - v3)) / ((v1 - v2) * (v0 - v3))


def _solve_unknown(known, u, target):
    x = sp.Symbol("x", real=True)
    vals = [Fraction(k, 1) for k in known]
    vals.insert(u, x)
    a, b, c, d = vals
    expr = ((a - c) * (b - d)) / ((b - c) * (a - d)) - Fraction(target)
    sols = sp.solve(sp.cancel(expr), x)
    if len(sols) != 1:
        return None
    v = sols[0]
    if not v.is_number or not v.is_real:
        return None
    f = Fraction(str(v))
    return f


def _render_frac(f):
    if f.denominator == 1:
        return str(f.numerator)
    return f"{f.numerator}/{f.denominator}"


def _parse_frac(s):
    s = s.strip()
    if "/" in s:
        return Fraction(s)
    return Fraction(int(s), 1)


@dataclass
class ProjectiveInvariantsConfig(Config):
    max_mag: int = 4
    frac_mag: int = 4

    def apply_difficulty(self, level):
        self.max_mag = 4 + 2 * level
        self.frac_mag = 4 + 2 * level


class ProjectiveConfigurationInvariants(Task):
    config_cls = ProjectiveInvariantsConfig
    summary = ("Compare labeled finite points on the real projective line; recover a missing "
               "integer or reduced-fraction coordinate from three known coordinates and a "
               "prescribed cross-ratio, using its invariance under fractional-linear changes.")
    design_choice = ("Use integer coordinates and ask for the missing coordinate value as a reduced fraction, with constraints chosen so the cross-ratio uniquely determines it.")

    def generate_entry(self):
        mm = self.config.max_mag
        fm = self.config.frac_mag
        known = [random.randint(-mm, mm) for _ in range(3)]
        u = random.randrange(4)
        if random.random() < 0.5:
            ghost = random.randint(-mm, mm)
            all_vals = list(known)
            all_vals.insert(u, ghost)
            if len(set(all_vals)) != 4:
                return self.generate_entry()
            target = _cr_frac(all_vals)
        else:
            target = Fraction(random.randint(1, fm), random.choice([1, random.randint(1, fm)]))
        sol = _solve_unknown(known, u, target)
        if sol is None:
            return self.generate_entry()
        answer = _render_frac(sol)
        prompt_known = [None, None, None, None]
        idx = 0
        for pos in range(4):
            if pos == u:
                prompt_known[pos] = None
            else:
                prompt_known[pos] = int(known[idx])
                idx += 1
        return Entry(metadata={
            "known": prompt_known,
            "target_cross_ratio": str(target),
            "unknown_position": int(u),
        }, answer=answer)

    def render_prompt(self, metadata):
        known = metadata["known"]
        pts = []
        for pos in range(4):
            v = known[pos]
            pts.append(f"P{pos}={v}" if v is not None else f"P{pos}=?")
        tgt = metadata["target_cross_ratio"]
        lines = "\n".join(f"  {t}" for t in pts)
        return (
            "Four labeled points P0, P1, P2, P3 on the real projective line have cross-ratio "
            "(P0,P1;P2,P3)=((P0-P2)(P1-P3))/((P1-P2)(P0-P3)), which is invariant under all "
            "fractional-linear (projective) coordinate changes between points on the line.\n"
            f"Their coordinates are:\n{lines}\n"
            f"Their cross-ratio (P0,P1;P2,P3) equals {tgt}.\n"
            "Give the missing coordinate as a reduced fraction (e.g. 3 or 5/2)."
        )

    def score_answer(self, answer, entry):
        try:
            given = _parse_frac(answer)
        except (ValueError, ZeroDivisionError):
            return 0.0
        target = _parse_frac(entry.answer)
        return 1.0 if given == target else 0.0
