from dataclasses import dataclass
import random

from sympy import Rational, Symbol

from reasoning_core.template import Task, Entry, Config, edict, render_payload

TASK_META = {'parent_source_id': None,
 'idea': 'dual_number_evaluation (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_state_tracking_r4/dual_number_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_X = Symbol('x')


def _coef_str(r):
    n = r.p
    d = r.q
    if d == 1:
        return str(n)
    return f'{n}/{d}'


def _render_poly(coeffs):
    terms = []
    deg = len(coeffs) - 1
    for i in range(len(coeffs) - 1, -1, -1):
        c = coeffs[i]
        if c == 0:
            continue
        abs_c = abs(c)
        sign = '-' if c < 0 else '+'
        if i == 0:
            term = _coef_str(abs_c)
        elif i == 1:
            term = (f'{_coef_str(abs_c)}' if abs_c != 1 else '') + 'x'
        else:
            term = (f'{_coef_str(abs_c)}' if abs_c != 1 else '') + f'x^{i}'
        terms.append((sign, term))
    if not terms:
        return '0'
    out = ''
    for idx, (sign, term) in enumerate(terms):
        prefix = '' if (idx == 0 and sign == '+') else sign
        out += f'{prefix}{term}'
    return out


def _rand_rational(rng, coeff_range, den_scale):
    while True:
        n = rng.randint(-coeff_range, coeff_range)
        d = rng.randint(1, den_scale)
        r = Rational(n, d)
        if r != 0 or rng.random() < 0.15:
            return r


def _build_poly(max_deg, coeff_range, den_scale):
    deg = rng_randint(0, max_deg)
    coeffs = []
    for _ in range(deg + 1):
        coeffs.append(_rand_rational(random, coeff_range, den_scale))
    if len(coeffs) == 1 and coeffs[0] == 0:
        coeffs[0] = Rational(random.choice([-1, 1]) * random.randint(1, coeff_range))
    return coeffs


def rng_randint(a, b):
    return random.randint(a, b)


def _fmt_pair(value, deriv):
    return f'{_coef_str(value)}; {_coef_str(deriv)}'


@dataclass
class DualNumberConfig(Config):
    max_deg: int = 2
    coeff_range: int = 3
    den_scale: int = 2
    point_den: int = 1

    def apply_difficulty(self, level):
        self.max_deg = 2 + level
        self.coeff_range = 3 + 2 * level
        self.den_scale = 2 + level
        self.point_den = 1 + level


class DualNumberEvaluation(Task):
    summary = ("Evaluate a rational function P/Q in dual numbers at an exact rational point x0, "
               "propagating the infinitesimal through sums, products, and quotients; answer "
               "is the exact f(x0) and f'(x0) reduced-fraction pair.")
    config_cls = DualNumberConfig

    def generate_entry(self):
        cfg = self.config
        while True:
            p_coeffs = _build_poly(cfg.max_deg, cfg.coeff_range, cfg.den_scale)
            q_coeffs = _build_poly(cfg.max_deg, cfg.coeff_range, cfg.den_scale)
            if all(c == 0 for c in q_coeffs):
                continue
            x0n = random.randint(-cfg.coeff_range, cfg.coeff_range)
            x0d = random.randint(1, cfg.point_den)
            x0 = Rational(x0n, x0d)

            P = sum(Rational(c) * _X ** i for i, c in enumerate(p_coeffs))
            Q = sum(Rational(c) * _X ** i for i, c in enumerate(q_coeffs))
            q0 = Q.subs(_X, x0)
            if q0 == 0:
                continue

            p0 = P.subs(_X, x0)
            Pp = P.diff(_X)
            Qp = Q.diff(_X)
            p1 = Pp.subs(_X, x0)
            q1 = Qp.subs(_X, x0)

            value = Rational(p0, q0)
            deriv = Rational(p1 * q0 - p0 * q1, q0 * q0)

            answer = _fmt_pair(value, deriv)

            metadata = edict({
                'p_str': _render_poly([Rational(c) for c in p_coeffs]),
                'q_str': _render_poly([Rational(c) for c in q_coeffs]),
                'point': _coef_str(x0),
                'p_coeffs': [str(Rational(c)) for c in p_coeffs],
                'q_coeffs': [str(Rational(c)) for c in q_coeffs],
                'value': _coef_str(value),
                'deriv': _coef_str(deriv),
            })
            metadata.payload = {'P': metadata.p_str, 'Q': metadata.q_str, 'x0': metadata.point}
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            "Dual numbers extend the reals with an infinitesimal element e satisfying e*e = 0; "
            "a dual number a + b*e represents a value a with infinitesimal part b. Evaluating a "
            "differentiable function f at the dual input x0 + e yields f(x0) + f'(x0)*e.\n\n"
            "Given the rational function R(x) = P(x)/Q(x) with rational coefficients below, "
            "evaluate R at the dual point x0 + e. Answer with the exact pair of reduced "
            "fractions 'value; derivative', i.e. f(x0); f'(x0). Write each rational as "
            "numerator/denominator with denominator positive, or as a plain integer when the "
            "denominator is 1 (zero is '0').\n\n"
            f"{render_payload(metadata.payload)}"
        )

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0
