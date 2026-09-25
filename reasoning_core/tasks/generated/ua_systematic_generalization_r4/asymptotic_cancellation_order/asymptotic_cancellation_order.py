import random
from dataclasses import dataclass

import sympy as sp

from reasoning_core.template import Config, Entry, Task


def _exp_of(key):
    if key == 1:
        return 0
    base, expo = key.as_base_exp()
    return expo


def _survivor(expr, x, n):
    ser = sp.series(expr, x, 0, n)
    poly = ser.removeO()
    d = poly.as_coefficients_dict()
    best = None
    for key, coeff in d.items():
        if coeff != 0:
            e = int(_exp_of(key))
            if best is None or e < best[0]:
                best = (e, sp.Rational(coeff))
    return best


def _coeff_str(frac):
    if frac.q == 1:
        return str(frac.p)
    return f"{frac.p}/{frac.q}"


def _rand_series(x, E, D):
    lo = random.randint(0, E)
    terms = []
    for j in range(D + 1):
        if j == 0:
            c = random.randint(1, 8)
        else:
            c = random.randint(-8, 8)
        if c:
            terms.append(c * x ** j)
    poly = sp.Add(*terms) if terms else sp.Integer(1)
    return x ** lo * poly


def _rand_analytic(x):
    b = random.randint(1, 3)
    choice = random.randint(0, 2)
    if choice == 0:
        return sp.exp(b * x) - 1
    if choice == 1:
        return sp.sin(b * x)
    return sp.log(1 + b * x)


@dataclass
class AsymptoticCancellationOrderConfig(Config):
    base_level: int = 0

    def apply_difficulty(self, level):
        self.base_level = level


class AsymptoticCancellationOrder(Task):
    summary = ("Find the first surviving asymptotic term (lowest nonzero coefficient) of nested "
               "sums, products, quotients, and analytic expansions of exact series about x=0, "
               "where leading orders cancel; return its integer exponent and rational coefficient.")
    config_cls = AsymptoticCancellationOrderConfig
    task_version = 2

    def generate_entry(self):
        x = sp.symbols("x")
        level = self.config.base_level
        E = min(level, 3)
        D = random.randint(0, 2)
        n = 10 + level
        for _ in range(80):
            lo = random.randint(1, 1 + min(level, 2))
            c0 = random.choice([i for i in range(-8, 9) if i != 0])
            s1 = x ** lo * (sp.Integer(c0) + _rand_series(x, E, D))
            s2 = x ** lo * (sp.Integer(c0) + _rand_series(x, E, D))
            expr = sp.expand(s1 - s2)
            if level and random.random() < 0.3:
                expr = sp.expand(_rand_analytic(x) + expr)
            depth = min(level, 4)
            for _k in range(depth):
                u = _rand_series(x, E, D)
                op = random.choice(["mul", "add", "sub", "mul", "add", "div"])
                if op == "mul":
                    expr = sp.expand(expr * u)
                elif op == "div":
                    expr = sp.expand(expr / u)
                elif op == "add":
                    expr = sp.expand(expr + u)
                else:
                    expr = sp.expand(expr - u)
                if expr.count_ops() > 160:
                    break
            surv = _survivor(expr, x, n + 4)
            if surv is None:
                continue
            e, coeff = surv
            if e >= n - 3 or e < 1:
                continue
            c_str = _coeff_str(coeff)
            return Entry(
                    metadata={
                        "expression": sp.sstr(expr),
                        "exp": e,
                        "coeff_str": c_str,
                        "coeff_num": int(coeff.p),
                        "coeff_den": int(coeff.q),
                        "order": n,
                    },
                    answer=f"{e}, {c_str}",
                )
        raise RuntimeError("asymptotic_cancellation_order: failed to generate an admissible instance")

    def render_prompt(self, metadata):
        return (
            "Consider the asymptotic expansion of the following expression about x = 0 "
            "(the Maclaurin/Laurent series). Successive leading orders cancel, leaving a "
            "first nonzero term.\n\n"
            f"Expression: {metadata['expression']}\n\n"
            "Find the first surviving (lowest-order) nonzero term of its expansion in "
            "powers of x. Report its exponent followed by its coefficient, as two "
            "comma-separated values, e.g. '3, -2/5'. The exponent is an integer and the "
            "coefficient is an exact rational."
        )

    def score_answer(self, answer, entry):
        ref_exp = entry.metadata["exp"]
        ref_frac = sp.Rational(entry.metadata["coeff_num"], entry.metadata["coeff_den"])
        try:
            text = str(answer).strip()
            if "," not in text:
                return 0.0
            exp_part, coeff_part = text.split(",", 1)
            cand_exp = int(exp_part.strip())
            coeff_part = coeff_part.strip().replace(" ", "")
            cand_frac = sp.Rational(coeff_part)
        except Exception:
            return 0.0
        if cand_exp != ref_exp or cand_frac != ref_frac:
            return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'asymptotic_cancellation_order (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/asymptotic_cancellation_order',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3143501959,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
