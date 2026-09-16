import random
from dataclasses import dataclass
from fractions import Fraction

import sympy as sp

from reasoning_core.template import Config, Entry, Task


@dataclass
class PartialFractionConfig(Config):
    n_linear: int = 2
    n_quad: int = 1
    coef_range: int = 20
    max_mult: int = 1

    def apply_difficulty(self, level):
        self.n_linear = 2 + min(level, 2)
        self.n_quad = 1 + min(level // 2, 1)
        self.max_mult = 1 + min(level // 2, 2)
        self.coef_range = 10 + 8 * min(level, 3)


_X = sp.Symbol("x")


def _frac_str(val):
    val = sp.nsimplify(val)
    r = sp.Rational(val)
    return f"{r.p}/{r.q}" if r.q != 1 else f"{r.p}"


def _lin(r):
    """Render (x - r) with correct sign, e.g. (x+3) for r=-3, (x) for r=0."""
    if r == 0:
        return "x"
    if r < 0:
        return f"(x+{-r})"
    return f"(x-{r})"


def _linpow(r, k):
    base = _lin(r)
    return base if k == 1 else f"{base}^{k}"


def _quad(b, c):
    """Render x^2 + b x + c with correct signs."""
    term = f"x^2"
    if b > 0:
        term += f"+{b}x"
    elif b < 0:
        term += f"-{-b}x"
    if c > 0:
        term += f"+{c}"
    elif c < 0:
        term += f"-{-c}"
    return term


def _quadpow(b, c, k):
    base = _quad(b, c)
    return base if k == 1 else f"({base})^{k}"

def _decompose(linear_factors, quad_factors, num_poly):
    """Return ordered slot descriptions and exact coefficient fractions.

    linear_factors: list of (root, mult). quad_factors: list of ((b, c), mult).
    num_poly: sympy polynomial (degree == deg(den)-1) to decompose.
    """
    full_den = sp.Integer(1)
    for r, e in linear_factors:
        full_den *= (_X - r) ** e
    for (b, c), e in quad_factors:
        full_den *= (_X ** 2 + b * _X + c) ** e

    slots = []
    symbols = []
    contributions = []

    for r, e in linear_factors:
        base = _X - r
        for k in range(1, e + 1):
            C = sp.Symbol(f"c_{len(symbols)}")
            symbols.append(C)
            q = sp.div(full_den, base ** k, _X)[0]
            contributions.append(C * q)
            slots.append(("lin", r, k))

    for (b, c), e in quad_factors:
        base = _X ** 2 + b * _X + c
        for k in range(1, e + 1):
            A = sp.Symbol(f"a_{len(symbols)}")
            B = sp.Symbol(f"b_{len(symbols) + 1}")
            symbols.extend([A, B])
            q = sp.div(full_den, base ** k, _X)[0]
            contributions.append((A + B * _X) * q)
            slots.append(("quad", (b, c), k))

    num_total = sum(contributions, sp.Integer(0))
    poly = sp.Poly(sp.expand(num_total), _X)
    nump = sp.Poly(sp.expand(num_poly), _X)

    degree = max(poly.degree(), nump.degree()) + 1
    eqs = [poly.nth(i) - nump.nth(i) for i in range(degree)]
    solset = sp.linsolve(eqs, symbols)
    if len(solset) != 1:
        raise RuntimeError("no unique decomposition")
    sol_tup = next(iter(solset))
    vals = dict(zip(symbols, sol_tup))

    for s, v in zip(symbols, sol_tup):
        if not v.is_Rational and v != sp.Integer(
                0):
            raise RuntimeError("non-rational coefficient generated")

    return slots, [_frac_str(vals[s]) for s in symbols]


class PartialFractionDecomposition(Task):
    summary = "Decompose proper rational functions into partial fractions over distinct and repeated linear or given irreducible quadratic factors, answering the exact per-term rational coefficients."
    design_choice = "Generate instances where the numerator degree is exactly one less than the denominator degree, ensuring a proper fraction, and require the decomposition to include both constant and linear numerator terms for repeated quadratic factors."
    config_cls = PartialFractionConfig

    def generate_entry(self):
        cfg = self.config
        cr = int(cfg.coef_range)
        while True:
            roots = random.sample(range(-cr, cr + 1), int(cfg.n_linear))
            quad_params = set()
            quads = []
            attempts = 0
            while len(quads) < int(cfg.n_quad) and attempts < 200:
                attempts += 1
                b = random.randint(-cfg.coef_range, cfg.coef_range)
                c = random.randint(1, cfg.coef_range * 2)
                if b * b - 4 * c >= 0:
                    continue
                key = (b, c)
                if key in quad_params:
                    continue
                quad_params.add(key)
                quads.append(key)

            linear_factors = [(r, random.randint(1, int(cfg.max_mult))) for r in roots]
            quad_factors = [(bc, random.randint(1, int(cfg.max_mult))) for bc in quads]

            total_deg = 0
            for r, e in linear_factors:
                total_deg += e
            for (b, c), e in quad_factors:
                total_deg += 2 * e

            coeffs = [random.randint(-cr, cr) for _ in range(total_deg)]
            coeffs[-1] = random.choice([d for d in range(-cr, cr + 1) if d != 0])
            num_poly = sum(cc * _X ** i for i, cc in enumerate(coeffs))

            try:
                slots, answer_fracs = _decompose(
                    linear_factors, quad_factors, num_poly
                )
            except Exception:
                continue

            answer_str = ",".join(answer_fracs)

            slot_desc = []
            for (kind, key, k) in slots:
                if kind == "lin":
                    r = key
                    slot_desc.append(f"C_{k}/{_linpow(r, k)}")
                else:
                    (b, c) = key
                    slot_desc.append(f"A_{k} (coefficient of 1/{_quadpow(b, c, k)})")
                    slot_desc.append(f"B_{k} (coefficient of x/{_quadpow(b, c, k)})")

            metadata = {
                "numerator": coeffs,
                "linear_factors": [(r, e) for r, e in linear_factors],
                "quad_factors": [[b, c, e] for (b, c), e in quad_factors],
                "slots": slot_desc,
                "answer": answer_fracs,
            }
            return Entry(metadata=metadata, answer=answer_str)

    def render_prompt(self, metadata):
        parts = metadata["numerator"]
        deg = len(parts) - 1
        def mono(i, cc):
            if cc == 0:
                return ""
            sgn = " - " if cc < 0 else " + "
            ab = abs(cc)
            if i == 0:
                return f"{sgn}{ab}"
            if i == 1:
                return f"{sgn}{ab}x" if ab != 1 else f"{sgn}x"
            return f"{sgn}{ab}x^{i}" if ab != 1 else f"{sgn}x^{i}"

        num_str = mono(deg, parts[-1]) + "".join(mono(i, cc) for i, cc in enumerate(parts[:-1]))
        num_str = num_str.lstrip(" +")

        den_terms = [_linpow(r, e) for r, e in metadata["linear_factors"]]
        den_terms += [_quadpow(b, c, e) for b, c, e in metadata["quad_factors"]]
        den_str = "*".join(den_terms)

        factor_lines = []
        idx = 1
        for r, e in metadata["linear_factors"]:
            if e == 1:
                factor_lines.append(f"{idx}. {_lin(r)} with multiplicity 1: C_1/{_lin(r)}")
            else:
                factor_lines.append(f"{idx}. {_lin(r)} with multiplicity {e}: C_1/{_lin(r)} + ... + C_{e}/{_linpow(r, e)}")
            idx += 1
        for b, c, e in metadata["quad_factors"]:
            base = _quad(b, c)
            factor_lines.append(f"{idx}. ({base}) with multiplicity {e}: sum over k of (A_k x + B_k)/({base})^k")
            idx += 1

        slot_list = "; ".join(metadata["slots"])

        prompt = (
            f"Express the proper rational function ({num_str})/({den_str}) as a sum of "
            "partial fractions, where a term (x-r)^k contributes C_k/(x-r)^k and a term "
            "(x^2+bx+c)^k contributes (A_k x + B_k)/(x^2+bx+c)^k. "
            "The irreducible factors and their ordered coefficient slots are:\n"
            + "\n".join(f"  {line}" for line in factor_lines)
            + "\n\n"
            f"In this order, the coefficient slots are: {slot_list}.\n"
            "Give the exact rational value of each coefficient, in the same order, "
            "comma-separated (a fraction as n/d or an integer), one value per slot."
        )
        return prompt

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.metadata["answer"]
        try:
            vals = [Fraction(p.strip()) for p in answer.split(",") if p.strip()]
        except Exception:
            return 0.0
        if len(vals) != len(gold):
            return 0.0
        for v, g in zip(vals, gold):
            if v != Fraction(g):
                return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'partial_fraction_decomposition (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/partial_fraction_decomposition',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
