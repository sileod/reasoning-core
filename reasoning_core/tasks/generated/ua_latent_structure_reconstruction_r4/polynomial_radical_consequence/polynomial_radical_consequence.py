import random
from dataclasses import dataclass

import sympy as sp

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'polynomial_radical_consequence (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_structure_reconstruction_r4/polynomial_radical_consequence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _linear_factor(v):
    if v >= 0:
        return f"(x - {v})"
    return f"(x + {-v})"


def _radical_membership_vanishes(eqs, q, gens):
    """True iff q vanishes on every complex common solution of the system.

    Rabinowitsch trick: q lies in the radical ideal <eqs> over an algebraically
    closed field iff 1 belongs to <eqs, 1 - t*q> in the ring extended by a new
    indeterminate t.  Membership is decided by a Groebner basis, so this is an
    exact (and conservative) check independent of the construction below.
    """
    t = sp.Symbol('t')
    gb = sp.groebner(list(eqs) + [1 - t * q], list(gens) + [t])
    return bool(gb.contains(sp.Integer(1)))


@dataclass
class PolynomialRadicalConsequenceConfig(Config):
    d: int = 3
    n_vars: int = 1
    max_exp: int = 1
    value_range: int = 5

    def apply_difficulty(self, level):
        self.d = 3 + level
        self.n_vars = min(3, 1 + level // 2)
        self.max_exp = 1 + level
        self.value_range = 5 + level


class PolynomialRadicalConsequence(Task):
    summary = ("Combine monomial, binomial, and coupled polynomial equations over complex "
               "variables; decide whether a queried polynomial vanishes on every common "
               "solution, distinguishing radical from ideal membership.")
    design_choice = ("Encode the query polynomial as a product of two factors and ask whether the "
                     "product vanishes on all solutions, forcing solvers to test both factors' "
                     "radical membership.")
    config_cls = PolynomialRadicalConsequenceConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        while True:
            entry = self._try_entry(cfg)
            if entry is not None:
                return entry

    def _try_entry(self, cfg):
        var_names = ['x', 'y', 'z'][:cfg.n_vars]
        gens = [sp.Symbol(v) for v in var_names]
        x = gens[0]

        lo, hi = -cfg.value_range, cfg.value_range
        s_vals = sorted(random.sample(range(lo, hi + 1), cfg.d))
        if 0 in s_vals:
            s_vals.remove(0)
            s_vals.append(0)
        s_vals.sort()

        eqs = [sp.expand(sp.Mul(*[(x - sp.Integer(v)) for v in s_vals]))]
        secondary = []
        for g in gens[1:]:
            kind = random.choice(['independent', 'coupled', 'monomial'])
            if kind == 'monomial':
                r = random.randint(2, cfg.max_exp)
                eqs.append(g ** r)
                secondary.append({'var': g.name, 'kind': 'monomial',
                                  'exp': r, 'values': [0]})
            elif kind == 'independent':
                d2 = random.randint(2, cfg.d)
                t_vals = sorted(random.sample(range(lo, hi + 1), d2))
                eqs.append(sp.expand(sp.Mul(*[(g - sp.Integer(w)) for w in t_vals])))
                secondary.append({'var': g.name, 'kind': 'independent',
                                  'exp': 1, 'values': t_vals})
            else:  # coupled: g = coef*x + const
                coef = random.choice([c for c in range(-3, 4) if c != 0])
                const = random.choice([c for c in range(-4, 5)])
                eqs.append(g - (coef * x + const))
                secondary.append({'var': g.name, 'kind': 'coupled',
                                  'exp': 1, 'coef': coef, 'const': const,
                                  'values': [coef * v + const for v in s_vals]})

        d = cfg.d
        target_yes = random.random() < 0.5
        if target_yes:
            a = sorted(random.sample(s_vals, random.randint(1, d - 1)))
            b = [v for v in s_vals if v not in a]
        else:
            a = sorted(random.sample(s_vals, random.randint(1, d - 2)))
            others = [v for v in s_vals if v not in a]
            b = sorted(random.sample(others, random.randint(1, len(others) - 1)))

        f = sp.expand(sp.Mul(*[(x - sp.Integer(v)) for v in a]))
        g = sp.expand(sp.Mul(*[(x - sp.Integer(v)) for v in b]))
        q = sp.expand(f * g)

        answer_yes = set(a) | set(b) == set(s_vals)
        if _radical_membership_vanishes(eqs, q, gens) != answer_yes:
            return None

        primary = {'var': 'x', 'kind': 'binomial', 'exp': 1, 'values': s_vals}
        metadata = {
            'primary': primary,
            'secondary': secondary,
            'eq_strings': [sp.sstr(e) for e in eqs],
            'factor_a': a,
            'factor_b': b,
            'q_string': sp.sstr(q),
            'answer_is_yes': answer_yes,
        }
        answer = 'Yes' if answer_yes else 'No'
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        var_names = ['x', 'y', 'z'][:len(metadata['secondary']) + 1]
        sys_lines = '\n'.join(f"  {e} = 0" for e in metadata['eq_strings'])
        f = ' * '.join(_linear_factor(v) for v in metadata['factor_a'])
        g = ' * '.join(_linear_factor(v) for v in metadata['factor_b'])
        return (
            f"Over the complex numbers, consider the polynomial system in {', '.join(var_names)}:\n"
            f"{sys_lines}\n"
            f"Let I be the ideal generated by these polynomials; its common zero set is a finite "
            f"collection of points in C^n.\n\n"
            f"Consider the product of two factors\n"
            f"  q = f * g,\n"
            f"  f = {f},\n"
            f"  g = {g}.\n\n"
            f"Decide whether q vanishes on EVERY common complex solution of the system, i.e. whether "
            f"q belongs to the radical of I (use the Rabinowitsch trick with a Groebner basis).\n\n"
            f"Answer Yes if it vanishes on every common solution, and No otherwise. "
            f"State your conclusion."
        )

    def score_answer(self, answer, entry):
        ref = str(entry['answer']).strip().upper()
        ans = str(answer).strip().upper()
        return 1.0 if ans == ref else 0.0
