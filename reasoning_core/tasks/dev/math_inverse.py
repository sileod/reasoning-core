"""Inverse-problem mathematics: sample the answer, apply the easy direction, ask for the hard one.

Differentiation, expansion, substitution and differencing are mechanical; their inverses
(integration, factoring, solving, summation) are where mathematical skill lives. One small
expression grammar seeds every mode, and every answer is checked semantically (derivative,
expansion + irreducibility, root sets, exact partial sums), so any correct form scores.
"""
import random
import re
from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor, implicit_multiplication_application, parse_expr, standard_transformations,
)

from reasoning_core.runtime import TimeoutException, timeout_retry
from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding

x, y, n, k = sp.symbols("x y n k")
_UNARY = [sp.exp, sp.log, sp.sqrt, sp.sin, sp.cos, sp.tan, sp.atan]
_FUNCS = {"exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt, "sin": sp.sin, "cos": sp.cos,
          "tan": sp.tan, "atan": sp.atan, "arctan": sp.atan, "asin": sp.asin, "acos": sp.acos,
          "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh, "abs": sp.Abs, "Abs": sp.Abs,
          "cot": sp.cot, "asinh": sp.asinh, "acosh": sp.acosh, "atanh": sp.atanh, "arcsin": sp.asin,
          "arccos": sp.acos, "arcsinh": sp.asinh, "arccosh": sp.acosh, "arctanh": sp.atanh,
          "pi": sp.pi, "E": sp.E, "e": sp.E, "binomial": sp.binomial, "factorial": sp.factorial}
_TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)
_SAFE = re.compile(r"^[\w\s+\-*/^().,]*$")


def normalize(text):
    """Plain-text form of common LaTeX / textbook notation, so correct answers are not lost to format."""
    t = str(text).strip()
    for a, b in [("\\(", ""), ("\\)", ""), ("\\[", ""), ("\\]", ""), ("$", ""), ("\\left", ""), ("\\right", ""),
                 ("\\cdot", "*"), ("\\times", "*"), ("\\,", " "), ("\\!", ""), ("\\ln", "log"), ("\\", ""),
                 ("\u2212", "-"), ("\u00b7", "*")]:
        t = t.replace(a, b)
    while re.search(r"d?frac\{", t):  # innermost \frac{a}{b} first
        t = re.sub(r"d?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", t)
        t = re.sub(r"sqrt\{([^{}]*)\}", r"sqrt(\1)", t)
        if not re.search(r"d?frac\{[^{}]*\}\{[^{}]*\}", t) and re.search(r"d?frac\{", t):
            t = re.sub(r"\{([^{}]*)\}", r"(\1)", t, count=1)
    t = re.sub(r"sqrt\{([^{}]*)\}", r"sqrt(\1)", t)
    t = re.sub(r"log_\{?(\d+)\}?\s*\(([^()]*)\)", r"(log(\2)/log(\1))", t)
    t = re.sub(r"log_\{?(\d+)\}?\s*(\w+)", r"(log(\2)/log(\1))", t)
    t = re.sub(r"\|([^|]+)\|", r"(abs(\1))", t)
    t = re.sub(r"C_\{?(\d)\}?", r"C\1", t).replace("±", "").replace("pm", "")  # C_1 -> C1; y = ±f: the + branch
    return t.replace("{", "(").replace("}", ")")


def show(e):
    return sp.sstr(e).replace("**", "^")


def parse(text, var=x):
    text = normalize(text).split("=")[-1].strip().rstrip(".")
    words = set(re.findall(r"[A-Za-z_]\w*", text))
    if len(text) > 600 or not _SAFE.match(text) or "__" in text or words - set(_FUNCS) - {var.name, "C"}:
        return None
    try:
        return parse_expr(text, local_dict={**_FUNCS, var.name: var, "C": sp.Integer(0)}, transformations=_TRANSFORMS)
    except Exception:
        return None


def _num(e, var, v):
    try:
        z = complex(sp.N(e.subs(var, v), 30))
    except (TypeError, ValueError, ZeroDivisionError):
        return None
    return z if abs(z) < 1e12 and z == z else None


def _real_points(e, var, count=6, lo=0.05, hi=3.0):
    pts = []
    for _ in range(60):
        v = sp.Rational(random.randint(int(lo * 1000), int(hi * 1000)), 1000)
        z = _num(e, var, v)
        if z is not None and abs(z.imag) < 1e-12:
            pts.append(v)
        if len(pts) == count:
            break
    return pts


def _close(a, b):
    return a is not None and b is not None and abs(a - b) <= 1e-7 * max(1.0, abs(b))


# ---------------------------------------------------------------- grammar

def random_expr(size, var=x, consts=(1, 2, 3, 4, 5)):
    """Random expression tree with `size` internal operators (Lample & Charton style)."""
    if size <= 0:
        return var if random.random() < 0.7 else sp.Integer(random.choice(consts))
    if random.random() < 0.35:
        f = random.choice(_UNARY)
        return f(random_expr(size - 1, var, consts))
    left = random.randint(0, size - 1)
    a, b = random_expr(left, var, consts), random_expr(size - 1 - left, var, consts)
    op = random.choice(["+", "+", "*", "*", "-", "/", "^"])
    if op == "^":
        return a ** random.choice([2, 3, -1, -2, sp.Rational(1, 2)])
    return {"+": a + b, "-": a - b, "*": a * b, "/": a / b}[op]


def _ops(e):
    return sp.count_ops(e)


def _simplest(e):
    cands = [e, sp.cancel(e), sp.factor(e)]
    try:
        cands.append(_timed_simplify(e))
    except Exception:
        pass
    return min(cands, key=lambda c: (len(sp.sstr(c)), sp.count_ops(c)))


@timeout_retry(seconds=1, attempts=1)
def _timed_simplify(e):
    return sp.simplify(e)


# ---------------------------------------------------------------- modes

_ELEMENTARY = {"exp", "log", "sin", "cos", "tan", "cot", "atan", "asin", "acos", "sinh", "cosh", "tanh", "asinh", "acosh", "atanh"}


_INVERSE = {sp.log: sp.exp, sp.exp: sp.log, sp.atan: sp.tan, sp.tan: sp.atan, sp.asin: sp.sin, sp.sin: sp.asin,
            sp.acos: sp.cos, sp.cos: sp.acos}


def _reducible(e):
    """f(g(u)) with g = f^-1 (also log(exp(a)*b)): artefacts that only look hard."""
    for node in sp.preorder_traversal(e):
        inv = _INVERSE.get(type(node))
        if inv and any(isinstance(a, inv) for a in [node.args[0], *sp.Mul.make_args(node.args[0])]):
            return True
    return False


def _elementary(e):
    return not e.has(sp.Integral, sp.Piecewise) and all(type(f).__name__ in _ELEMENTARY for f in e.atoms(sp.Function))


@timeout_retry(seconds=1, attempts=1)
def _timed_integrate(f):
    return sp.integrate(f, x)


def gen_integral(size):
    if random.random() < 0.5:  # forward: a natural short integrand, whatever its antiderivative looks like
        size = max(1, size * 2 // 3)  # sympy's integrator is the cost; long forward integrands mostly time out
        f = random_expr(size)
        if x not in f.free_symbols or f.has(sp.zoo, sp.nan, sp.I) or _ops(f) < size or _reducible(f):
            return None
        F = _timed_integrate(f)
        if not _elementary(F) or len(show(F)) > 160 or not _real_points(f, x):
            return None
        return {"mode": "integral", "integrand": show(f)}, show(F)
    F = random_expr(size)
    F = F - F.as_independent(x, as_Add=True)[0]
    if _reducible(F):
        return None
    if _ops(F) < size or x not in F.free_symbols or F.has(sp.zoo, sp.nan, sp.I) or F.is_polynomial(x) and sp.degree(F, x) < 3:
        return None
    f = _simplest(sp.diff(F, x))
    if _reducible(f) or f == 0 or len(show(f)) > 220 or not _real_points(f, x):
        return None
    return {"mode": "integral", "integrand": show(f)}, show(F)


def score_integral(answer, meta):
    f, got = parse(meta["integrand"]), parse(answer)
    if got is None or got.has(sp.Integral) or f is None:
        return 0.0
    got = got.replace(lambda e: isinstance(e, sp.log) and isinstance(e.args[0], sp.Abs), lambda e: sp.log(e.args[0].args[0]))
    d = sp.diff(got, x)
    pts = _real_points(f, x)
    return float(bool(pts) and all(_close(_num(d, x, v), _num(f, x, v)) for v in pts))


def _irreducible(size, var_pool):
    for _ in range(50):
        deg = random.choice([1, 1, 2, 2, 3])
        vs = random.sample(var_pool, random.randint(1, len(var_pool)))
        terms = [random.randint(-4, 4) * sp.prod(random.choice(vs) ** random.randint(0, 1) for _ in range(deg))
                 for _ in range(random.randint(2, 2 + size // 2))]
        p = sp.expand(sum(terms) + random.choice(vs) ** deg)
        if p.free_symbols and sp.Poly(p, *var_pool).is_irreducible and sp.Poly(p, *var_pool).total_degree() > 0:
            return sp.Poly(p, *var_pool).as_expr()
    return None


def gen_factor(size):
    var_pool = [x] if random.random() < 0.6 or size < 2 else [x, y]
    count = 2 + random.randint(0, max(0, size // 2))
    factors = [_irreducible(size, var_pool) for _ in range(count)]
    if None in factors:
        return None
    lead = random.choice([1, 1, 2, 3, -1, 6])
    P = sp.expand(lead * sp.prod(f ** random.choice([1, 1, 1, 2]) for f in factors))
    if len(show(P)) > 400 or len(sp.Add.make_args(P)) < 3:
        return None
    return {"mode": "factor", "poly": show(P), "vars": [v.name for v in var_pool]}, show(sp.factor(P))


def score_factor(answer, meta):
    var_pool = sp.symbols(meta["vars"])
    got = _parse_poly(answer, var_pool)
    P = _parse_poly(meta["poly"], var_pool)
    if got is None or P is None or sp.expand(got - P) != 0:
        return 0.0
    for base in _leaf_factors(got):
        poly = sp.Poly(sp.expand(base), *var_pool)
        if poly.total_degree() == 0:
            continue
        if not (poly.is_irreducible and all(c.is_integer for c in poly.coeffs()) and abs(poly.content()) == 1):
            return 0.0
    return 1.0


def _leaf_factors(e):
    """Factors of an unevaluated product, looking through signs, nested products and integer powers."""
    if isinstance(e, sp.Mul):
        return [f for a in e.args for f in _leaf_factors(a)]
    if isinstance(e, sp.Pow):
        if not (e.exp.is_Integer and e.exp > 0):
            return [sp.Integer(0) * x + x ** sp.Rational(1, 2)]  # not a polynomial factorization
        return _leaf_factors(e.base)
    return [] if e.is_number else [e]


def _parse_poly(text, var_pool):
    text = normalize(text).split("=")[-1]
    names = {v.name: v for v in var_pool}
    if len(text) > 600 or not _SAFE.match(text) or set(re.findall(r"[A-Za-z_]\w*", text)) - set(names):
        return None
    try:
        return parse_expr(text, local_dict=names, transformations=_TRANSFORMS, evaluate=False)
    except Exception:
        return None


_SUBS = [  # (h(x), inverse image of t, valid t range)
    (lambda u: sp.exp(u), lambda t: sp.log(t), lambda t: t > 0),
    (lambda u: 2 ** u, lambda t: sp.log(t, 2), lambda t: t > 0),
    (lambda u: sp.log(u), lambda t: sp.exp(t), lambda t: True),
    (lambda u: sp.sqrt(u), lambda t: t ** 2, lambda t: t >= 0),
    (lambda u: 1 / u, lambda t: 1 / t, lambda t: t != 0),
    (lambda u: u ** 3, lambda t: sp.real_root(t, 3), lambda t: True),
    (lambda u: u + random.randint(1, 4), None, None),
    (lambda u: random.choice([2, 3, -2]) * u - random.randint(1, 5), None, None),
]


def gen_equation(size):
    roots = random.sample([sp.Rational(r, d) for r in range(-6, 7) for d in (1, 1, 1, 2, 3)], random.randint(1, 1 + min(size, 3) // 1))
    roots = sorted(set(roots))
    t = sp.Symbol("t")
    p = sp.prod(t - r for r in roots) * (t ** 2 + random.randint(1, 5) if random.random() < 0.3 else 1)
    chain, h = [], x
    for _ in range(1 + size // 2):
        i = random.randrange(len(_SUBS))
        g, inv, ok = _SUBS[i]
        if inv is None:  # affine maps, inverse computed symbolically
            u = sp.Symbol("u")
            gu = g(u)
            inv, ok = (lambda gu=gu, u=u: lambda s: sp.solve(sp.Eq(gu, s), u)[0])(), (lambda s: True)
            g = (lambda gu=gu, u=u: lambda v: gu.subs(u, v))()
        chain.append((inv, ok))
        h = g(h)
    sols = []
    for r in roots:
        vals = [r]
        for inv, ok in reversed(chain):
            vals = [inv(v) for v in vals if v.is_real and ok(v)]
        sols += [sp.nsimplify(v) if v.is_Rational else v for v in vals]
    sols = [s for s in sols if s.is_real and _num(h, x, s) is not None]
    lhs = sp.expand(p.subs(t, h), power_exp=False, power_base=False, log=False)
    if lhs.is_polynomial(x) and sp.degree(lhs, x) <= 2 or len(show(lhs)) > 300:
        return None
    terms = list(sp.Add.make_args(lhs))
    moved = [s for s in terms if random.random() < 0.3]
    left, right = sp.Add(*[s for s in terms if s not in moved]), -sp.Add(*moved)
    ans = ", ".join(show(s) for s in sorted(sols, key=lambda s: float(s))) or "none"
    return {"mode": "equation", "lhs": show(left), "rhs": show(right),
            "solutions": [show(s) for s in sols]}, ans


def score_equation(answer, meta):
    want = [complex(sp.N(parse(s))) for s in meta["solutions"]]
    text = normalize(str(answer).strip().strip("{}[]").replace("\\{", "").replace("\\}", "")).lower()
    if not want:
        return float(text in ("none", "no solution", "no real solution", "{}", "∅"))
    got = [parse(p) for p in re.split(r"[;,]", text.strip("{}[] ")) if p.strip()]
    if any(g is None or g.free_symbols for g in got) or len(got) != len(want):
        return 0.0
    got = [complex(sp.N(g)) for g in got]
    return float(all(any(_close(g, w) for g in got) for w in want) and all(any(_close(g, w) for w in want) for g in got))


def _discrete_term(size):
    kind = random.choice(["poly", "geom", "frac", "frac", "polygeom"])
    c = random.choice([1, 1, 2, 3, -1, sp.Rational(1, 2)])
    if kind == "poly":
        return c * n ** random.randint(2, 3 + size // 2)
    if kind == "geom":
        return c * random.choice([2, 3, sp.Rational(1, 2)]) ** n
    if kind == "polygeom":
        return c * n ** random.randint(1, 1 + size // 3) * random.choice([2, 3]) ** n
    a = random.randint(0, 3)
    return c * n ** random.randint(0, 1) / ((n + a + 1) * (n + a + random.randint(2, 3))) if random.random() < 0.5 else c / (n + a + 1)


@timeout_retry(seconds=1, attempts=1)
def _timed_summation(term):
    return sp.summation(term, (k, 1, n))


def _natural_term(size):
    pieces = [k ** random.randint(1, 3), random.choice([2, 3, sp.Rational(1, 2)]) ** k,
              k * random.choice([2, 3, sp.Rational(1, 2)]) ** k,
              1 / ((k + random.randint(0, 2)) * (k + random.randint(3, 5))),
              (2 * k + 1) * random.choice([1, -1]) ** k, sp.binomial(k + random.randint(0, 3), random.randint(1, 3))]
    return sum(random.choice([1, 2, 3, -1]) * p for p in random.sample(pieces, min(len(pieces), 1 + size // 3)))


def gen_sum(size):
    if random.random() < 0.5:  # forward: a short natural term, summed by sympy
        term = sp.expand_func(_natural_term(size))
        S = _timed_summation(term)
        S = _simplest(sp.expand_func(S))
        if not _elementary(S) or S.has(sp.Sum) or len(show(S)) > 200:
            return None
        return {"mode": "sum", "term": show(term)}, show(S)
    F = sum(_discrete_term(size) for _ in range(1 + size // 3))
    f = _simplest(sp.factor(sp.together(F - F.subs(n, n - 1))))
    if f == 0 or len(show(f)) > 220:
        return None
    return {"mode": "sum", "term": show(f.subs(n, k))}, show(sp.simplify(F - F.subs(n, 0)))


def score_sum(answer, meta):
    got, term = parse(answer, n), parse(meta["term"], k)
    if got is None or term is None:
        return 0.0
    total = sp.Integer(0)
    for m in range(1, 8):
        total += term.subs(k, m)
        try:
            if sp.nsimplify(sp.simplify(got.subs(n, m) - total)) != 0:
                return 0.0
        except Exception:
            return 0.0
    return 1.0


def gen_recurrence(size):
    """Closed form sum c_i n^j r_i^n (+ a forcing part) -> the linear recurrence it satisfies."""
    E = sp.Symbol("E")
    roots = random.sample([-3, -2, -1, 2, 3, 4, sp.Rational(1, 2)], random.randint(1, min(3, 1 + size // 2)))
    mults = {r: 1 + (random.random() < 0.25 * size / 3) for r in roots}
    hom = sum(random.choice([1, 2, -1, 3, sp.Rational(1, 2)]) * n ** j * r ** n for r in roots for j in range(mults[r]))
    forcing_bases = [b for b in (5, 1, -4) if b not in roots]
    part = 0
    if random.random() < 0.5:
        b = random.choice(forcing_bases)
        part = (n ** random.randint(0, 1) if b == 1 else 1) * b ** n * random.choice([1, 2, -1])
    closed = hom + part
    charpoly = sp.expand(sp.prod((E - r) ** m for r, m in mults.items()))
    coeffs = sp.Poly(charpoly, E).all_coeffs()  # leading 1
    d = len(coeffs) - 1
    shift = lambda f, j: f.subs(n, n + j)
    forcing = sp.simplify(sum(c * shift(part, d - i) for i, c in enumerate(coeffs))) if part else 0
    rhs = -sum(c * sp.Symbol(f"a(n+{d - i})" if d - i else "a(n)") for i, c in enumerate(coeffs[1:], 1)) + forcing
    inits = [sp.simplify(closed.subs(n, i)) for i in range(d)]
    if d < 2 and not part:
        return None
    return ({"mode": "recurrence", "order": d, "rhs": show(rhs).replace("a(n+0)", "a(n)"),
             "init": [show(v) for v in inits], "values": [show(sp.simplify(closed.subs(n, i))) for i in range(12)]},
            show(sp.simplify(closed)))


def score_recurrence(answer, meta):
    got = parse(answer, n)
    if got is None:
        return 0.0
    return float(all(sp.simplify(got.subs(n, i) - sp.sympify(v)) == 0 for i, v in enumerate(meta["values"])))


_PHI = [  # invertible outer maps: (phi, phi^{-1})
    (lambda u: u, lambda v: v), (sp.exp, sp.log), (sp.log, sp.exp), (lambda u: 1 / u, lambda v: 1 / v),
    (lambda u: u ** 3, lambda v: v ** sp.Rational(1, 3)), (sp.tan, sp.atan), (sp.sqrt, lambda v: v ** 2),
]
Y, C = sp.Function("y"), sp.Symbol("C")


C1, C2 = sp.symbols("C1 C2")


def gen_ode2(size):
    """y'' + p y' + q y = g from a chosen characteristic spectrum and particular solution (resonance included)."""
    kind = random.choice(["real", "repeated", "complex"])
    if kind == "real":
        r1, r2 = random.sample(range(-3, 4), 2)
        basis, (p, q) = [sp.exp(r1 * x), sp.exp(r2 * x)], (-(r1 + r2), r1 * r2)
    elif kind == "repeated":
        r1 = random.randint(-3, 3)
        basis, (p, q) = [sp.exp(r1 * x), x * sp.exp(r1 * x)], (-2 * r1, r1 * r1)
    else:
        a, b = random.randint(-1, 1), random.randint(1, 3)
        r1 = None
        basis, (p, q) = [sp.exp(a * x) * sp.cos(b * x), sp.exp(a * x) * sp.sin(b * x)], (-2 * a, a * a + b * b)
    forcing = [sum(random.randint(-3, 3) * x ** j for j in range(2 + size // 3)),
               random.randint(1, 3) * sp.exp(random.choice([-2, 1, 2, 4]) * x),
               random.randint(1, 3) * random.choice([sp.sin, sp.cos])(random.randint(1, 4) * x)]
    if r1 is not None:
        forcing.append(x ** (1 + (kind == "repeated")) * sp.exp(r1 * x))  # resonant: a particular solution needs extra x's
    L = lambda u: sp.diff(u, x, 2) + p * sp.diff(u, x) + q * u
    forcing = [f for f in forcing if sp.simplify(L(f)) != 0]  # homogeneous terms would vanish from the equation
    yp = sum(random.sample(forcing, min(len(forcing), 1 + size // 3)))
    g = _simplest(L(yp))
    if g == 0:
        return None
    lhs = sp.Derivative(Y(x), (x, 2)) + p * sp.Derivative(Y(x), x) + q * Y(x)
    term = lambda c, name: "" if c == 0 else f" {'-' if c < 0 else '+'} " + (name if abs(c) == 1 else f"{abs(c)}*{name}")
    dy = "y'"
    text = f"y''{term(p, dy)}{term(q, 'y')} = {show(g)}"
    if len(text) > 260:
        return None
    return ({"mode": "ode", "order": 2, "ode": text, "ode_lhs": sp.srepr(lhs - g)},
            show(C1 * basis[0] + C2 * basis[1] + yp))


def gen_ode(size):
    """Sample a one-parameter family y(x, C); eliminate C to get a first-order ODE (or a second-order linear one)."""
    if random.random() < 0.4:
        return gen_ode2(size)
    A = random_expr(max(1, size + size // 2 - 1))
    A = A - A.as_independent(x, as_Add=True)[0]  # additive constants are absorbed by C
    if x not in A.free_symbols:
        return None
    if random.random() < 0.5:  # separable: phi^{-1}(y) = A(x) + C
        phi, inv = random.choice(_PHI)
        sol = phi(A + C)
        ode = sp.Eq(sp.diff(inv(Y(x)), x), sp.diff(A, x))
    else:  # linear: y = B(x) (C + A(x))
        B = random.choice([sp.exp(random.choice([1, 2, -1]) * x), x ** random.choice([1, 2, -1]), sp.exp(x ** 2), sp.cos(x) ** -1])
        sol = B * (C + A)
        ode = sp.Eq(sp.diff(Y(x), x), sp.simplify(sp.diff(B, x) / B) * Y(x) + _simplest(B * sp.diff(A, x)))
    lhs, rhs = _simplest(ode.lhs), _simplest(ode.rhs)
    text = f"{show(lhs)} = {show(rhs)}".replace("Derivative(y(x), x)", "y'").replace("y(x)", "y")
    if len(text) > 260 or "Derivative" in text or "Subs" in text:
        return None
    return {"mode": "ode", "ode": text, "ode_lhs": sp.srepr(lhs - rhs)}, show(sol)


def score_ode(answer, meta):
    consts = [C1, C2] if meta.get("order") == 2 else [C]
    got = _parse_with_c(normalize(answer).split("=")[-1], consts)
    if got is None or set(consts) - got.free_symbols:
        return 0.0
    resid = sp.sympify(meta["ode_lhs"], locals={"y": Y, "x": x})
    for vals in ([sp.Rational(1, 3), sp.Rational(3, 2)], [sp.Rational(3, 2), -sp.Rational(1, 2)])[: 2]:
        yc = got.subs(dict(zip(consts, vals)))
        r = resid.subs(sp.Derivative(Y(x), (x, 2)), sp.diff(yc, x, 2)).subs(sp.Derivative(Y(x), x), sp.diff(yc, x)).subs(Y(x), yc)
        pts = _real_points(yc, x, count=4, lo=0.1, hi=1.2)
        if len(pts) < 2 or not all(_close(_num(r, x, v), 0j) for v in pts):
            return 0.0
    if len(consts) == 2:  # a genuinely two-parameter family: the C1, C2 directions are independent
        J = sp.Matrix([[sp.diff(got, c).subs(x, v) for c in consts] for v in (sp.Rational(1, 3), sp.Rational(4, 3))])
        if abs(complex(sp.N(J.det()))) < 1e-9:
            return 0.0
    return 1.0


def _parse_with_c(text, consts=(None,)):
    consts = [c for c in consts if c is not None] or [C]
    names = {c.name: c for c in consts}
    words = set(re.findall(r"[A-Za-z_]\w*", text))
    if len(text) > 600 or not _SAFE.match(text) or "__" in text or words - set(_FUNCS) - {"x"} - set(names):
        return None
    try:
        return parse_expr(text, local_dict={**_FUNCS, "x": x, **names}, transformations=_TRANSFORMS)
    except Exception:
        return None


def gen_minimum(size, certificate=False):
    """f = c + sum w_i q_i^2 with every q_i vanishing at a hidden point: min f = c, attained there."""
    vs = [x] if size < 2 or random.random() < 0.4 else [x, y]
    point = {v: sp.Rational(random.randint(-4, 4), random.choice([1, 1, 2])) for v in vs}
    squares = []
    for _ in range(max(len(vs), 1 + size // 2)):  # enough squares that no single one gives the answer away
        q = sum(random.randint(-3, 3) * sp.prod(random.choice(vs + [1]) for _ in range(random.randint(1, 1 + size // 3)))
                for _ in range(random.randint(2, 3)))
        q = sp.expand(sp.sympify(q) - sp.sympify(q).subs(point))
        if len(sp.Add.make_args(q)) >= 2:
            squares.append(random.choice([1, 1, 2, 3, sp.Rational(1, 2)]) * q ** 2)
    c = sp.Rational(random.randint(-20, 20), random.choice([1, 1, 2, 4]))
    f = sp.expand(c + sum(squares))
    if len(squares) < max(len(vs), 1 + size // 2) or set(vs) - f.free_symbols or len(show(f)) > 300:
        return None
    if certificate:  # ask for the proof itself: an SOS certificate of f >= c
        return ({"mode": "sos", "f": show(f), "bound": show(c), "vars": [v.name for v in vs]},
                " + ".join(show(t) for t in squares))
    return {"mode": "minimum", "f": show(f), "vars": [v.name for v in vs], "min": str(c)}, show(c)


def score_sos(answer, meta):
    """Valid iff the answer is a sum of w*(polynomial)^2 with w > 0 that expands to f - bound."""
    var_pool = sp.symbols(meta["vars"])
    got = _parse_poly(answer, var_pool)
    f, bound = _parse_poly(meta["f"], var_pool), sp.sympify(meta["bound"].replace("^", "**"))
    if got is None or f is None or sp.expand(got - (f - bound)) != 0:
        return 0.0
    for term in sp.Add.make_args(got):
        if term.is_number:
            if term < 0:
                return 0.0
            continue
        coeff, rest = sp.Integer(1), []
        for a in _flat_mul(term):
            if a.is_number:
                coeff *= a
            else:
                rest.append(a)
        # w * product of even powers is w * (product of half powers)^2
        if not (coeff > 0 and rest and all(isinstance(r, sp.Pow) and r.exp.is_Integer and r.exp > 0 and r.exp % 2 == 0
                                           for r in rest)):
            return 0.0
    return 1.0


def gen_claim(size):
    """Claim f >= b: true (answer: an SOS proof of f - b) or false (answer: a point where f < b)."""
    out = gen_minimum(size, certificate=True)
    if out is None:
        return None
    meta, sos = out
    c, vs = sp.sympify(meta["bound"].replace("^", "**")), sp.symbols(meta["vars"])
    delta = sp.Rational(random.randint(1, 6), random.choice([1, 2, 4]))
    if random.random() < 0.5:
        b = c - delta * random.randint(0, 1)
        proof = sos + (f" + {show(c - b)}" if c != b else "")
        return {**meta, "mode": "claim", "bound": show(b)}, f"proof: {proof}"
    f = sp.sympify(meta["f"].replace("^", "**"))
    for _ in range(200):  # any point strictly below b refutes the claim; report the nearest-to-origin one we find
        pt = {v: sp.Rational(random.randint(-8, 8), random.choice([1, 2])) for v in vs}
        if f.subs(pt) < c + delta:
            return ({**meta, "mode": "claim", "bound": show(c + delta)},
                    "counterexample: " + ", ".join(f"{v} = {show(pt[v])}" for v in vs))
    return None


def score_claim(answer, meta):
    text = normalize(answer).strip()
    head, _, body = text.partition(":")
    head = head.strip().lower()
    if head.startswith("proof"):
        return score_sos(body, {**meta, "mode": "sos"})
    if head.startswith("counterexample"):
        vs = sp.symbols(meta["vars"])
        pt = {}
        for part in re.split(r"[,;]", body):
            name, _, val = part.partition("=")
            v = next((s for s in vs if s.name == name.strip()), None)
            got = parse(val) if v is not None else None
            if got is None or got.free_symbols or not got.is_real:
                return 0.0
            pt[v] = got
        if set(pt) != set(vs):
            return 0.0
        f, b = sp.sympify(meta["f"].replace("^", "**")), sp.sympify(meta["bound"].replace("^", "**"))
        return float(bool(sp.nsimplify(f.subs(pt) - b) < 0))
    return 0.0


def _flat_mul(e):
    return [f for a in e.args for f in _flat_mul(a)] if isinstance(e, sp.Mul) else [e]


def score_minimum(answer, meta):
    got = parse(answer)
    return float(got is not None and not got.free_symbols and _close(complex(sp.N(got)), complex(sp.N(sp.sympify(meta["min"])))))


def gen_eigen(size):
    """A = P D P^-1 with P unimodular (random integer row operations): integer A, known spectrum."""
    d = min(5, 2 + size // 2)
    eig = [random.randint(-5, 5) for _ in range(d)]
    if random.random() < 0.3:
        eig[1] = eig[0]  # repeated eigenvalue
    P = sp.eye(d)
    for _ in range(2 * d + size):
        i, j = random.sample(range(d), 2)
        P[i, :] += random.choice([-2, -1, 1, 2]) * P[j, :]
    A = P * sp.diag(*eig) * P.inv()
    if len(set(eig)) == 1 or A.is_upper or A.is_lower or max(abs(v) for v in A) > 60 or sum(v != 0 for v in A) < d * d // 2:
        return None
    rows = "; ".join("[" + ", ".join(str(v) for v in A.row(i)) + "]" for i in range(d))
    return {"mode": "eigen", "matrix": rows, "eigenvalues": sorted(eig)}, ", ".join(map(str, sorted(eig)))


def score_eigen(answer, meta):
    parts = [p for p in re.split(r"[,;\s]+", normalize(answer).strip().strip("[]{}()")) if p]
    try:
        got = sorted(sp.Rational(p) for p in parts)
    except (TypeError, ValueError):
        return 0.0
    return float(got == sorted(sp.Rational(v) for v in meta["eigenvalues"]))


def _rand_poly(deg, vs, terms):
    return sp.expand(sum(random.randint(-3, 3) * sp.prod(random.choice(vs) for _ in range(random.randint(0, deg)))
                         for _ in range(terms)))


def gen_ideal(size):
    """g = a*f1 + b*f2 expanded: the cofactors (a, b) are a proof that f1 = f2 = 0 implies g = 0."""
    vs = [x, y]
    f1, f2 = (_rand_poly(random.randint(1, 2), vs, random.randint(2, 3)) for _ in range(2))
    a, b = (_rand_poly(min(3, 1 + size // 2), vs, random.randint(1, 2 + size // 2)) for _ in range(2))
    g = sp.expand(a * f1 + b * f2)
    if not (f1.free_symbols and f2.free_symbols and a != 0 and b != 0 and len(sp.Add.make_args(g)) >= 3) \
            or sp.expand(sp.cancel(g / f1)).is_polynomial(*vs) or sp.expand(sp.cancel(g / f2)).is_polynomial(*vs) \
            or len(show(g)) > 300:
        return None  # a multiple of a single generator would make one cofactor zero
    return {"mode": "ideal", "f1": show(f1), "f2": show(f2), "g": show(g)}, f"a = {show(a)}, b = {show(b)}"


def score_ideal(answer, meta):
    parts = dict(p.split("=", 1) for p in re.split(r"[,;]\s*(?=[ab]\s*=)", normalize(answer)) if "=" in p)
    parts = {k.strip(): v for k, v in parts.items()}
    if set(parts) != {"a", "b"}:
        return 0.0
    vs = [x, y]
    a, b = _parse_poly(parts["a"], vs), _parse_poly(parts["b"], vs)
    f1, f2, g = (_parse_poly(meta[k], vs) for k in ("f1", "f2", "g"))
    if None in (a, b, f1, f2, g):
        return 0.0
    return float(sp.expand(a * f1 + b * f2 - g) == 0)


_MODES = {"integral": (lambda size: gen_integral(size + size // 2), score_integral), "factor": (gen_factor, score_factor),
          "equation": (gen_equation, score_equation), "sum": (gen_sum, score_sum),
          "recurrence": (gen_recurrence, score_recurrence), "ode": (gen_ode, score_ode),
          "minimum": (gen_minimum, score_minimum), "sos": (lambda size: gen_minimum(size, True), score_sos),
          "claim": (gen_claim, score_claim), "eigen": (gen_eigen, score_eigen),
          "ideal": (gen_ideal, score_ideal)}


def score_inverse(answer, entry):
    meta = entry["metadata"]
    try:
        return _MODES[meta["mode"]][1](answer, meta)
    except Exception:
        return 0.0


@dataclass
class InverseMathConfig(Config):
    size: float = 1.0

    def apply_difficulty(self, level):
        self.size += 0.8 * level


class InverseMath(DevTask):
    summary = "Solve inverse problems generated from sampled answers: antiderivatives, complete integer factorizations, real solutions of substituted polynomial equations, closed forms of telescoped sums and linear recurrences, general solutions of first- and second-order ODEs, minima of expanded sums of squares with sum-of-squares proofs or counterexamples, eigenvalues of integer matrices, and ideal-membership cofactors proving polynomial implications."
    config_cls = InverseMathConfig
    task_version = 2

    def generate_entry(self):
        mode = random.choice(list(_MODES))  # drawn once: retrying per attempt would skew toward easy-to-hit modes
        for _ in range(200):
            try:
                out = _MODES[mode][0](max(1, stochastic_rounding(self.config.size)))
            except Exception:  # sympy raises many internal error types; a failed draw is just rejected
                continue
            if out and _MODES[mode][1](out[1], out[0]) == 1:  # the reference must pass its own checker
                return Entry(metadata=out[0], answer=out[1])
        raise RuntimeError("inverse_math: no instance after 200 attempts")

    def render_prompt(self, m):
        return self._question(m) + "\nUse plain notation, e.g. 3*x^2*exp(x) + log(x)/2."

    def _question(self, m):
        mode = m["mode"]
        if mode == "integral":
            return f"Find an antiderivative F(x) of f(x) = {m['integrand']}.\nThe answer is an expression in x (omit the constant)."
        if mode == "factor":
            return (f"Factor completely over the integers: {m['poly']}\n"
                    "The answer is a product of irreducible integer polynomials (and an integer constant).")
        if mode == "equation":
            return (f"Find all real solutions x of: {m['lhs']} = {m['rhs']}\n"
                    "The answer is the exact solutions separated by commas, or none.")
        if mode == "sum":
            return (f"Give a closed form in n for the sum over k = 1..n of {m['term']}.\n"
                    "The answer is an expression in n.")
        if mode == "recurrence":
            init = ", ".join(f"a({i}) = {v}" for i, v in enumerate(m["init"]))
            return (f"The sequence a satisfies a(n+{m['order']}) = {m['rhs']} for n >= 0, with {init}.\n"
                    "Give a closed form for a(n). The answer is an expression in n.")
        if mode == "ideal":
            return (f"Let f1 = {m['f1']} and f2 = {m['f2']}. Prove that f1 = 0 and f2 = 0 imply g = 0, where "
                    f"g = {m['g']}, by giving polynomials a, b in x, y with g = a*f1 + b*f2.\n"
                    "The answer has the form 'a = ..., b = ...'.")
        if mode == "eigen":
            return (f"Find all eigenvalues of the matrix with rows {m['matrix']}.\n"
                    "The answer is the eigenvalues in increasing order, repeated according to algebraic multiplicity, separated by commas.")
        if mode == "claim":
            return (f"Claim: f = {m['f']} satisfies f >= {m['bound']} for all real {', '.join(m['vars'])}.\n"
                    "Prove or refute it. If true, answer 'proof: ' followed by f - (" + m["bound"] + ") written as a sum of "
                    "terms w*(polynomial)^2 and positive constants, each w positive. If false, answer 'counterexample: ' "
                    "followed by values, e.g. 'counterexample: " + ", ".join(f"{v} = 1" for v in m["vars"]) + "'.")
        if mode == "sos":
            return (f"Prove that f = {m['f']} satisfies f >= {m['bound']} for all real {', '.join(m['vars'])}: "
                    f"write f - ({m['bound']}) as a sum of terms w*(polynomial)^2 with each w a positive number.\n"
                    "The answer is that sum.")
        if mode == "minimum":
            over = "real x" if len(m["vars"]) == 1 else "all real x, y"
            return f"Find the minimum value of f = {m['f']} over {over}.\nThe answer is an exact number."
        consts = "two arbitrary constants C1 and C2" if m.get("order") == 2 else "one arbitrary constant C"
        return (f"Find the general solution y(x) of the differential equation {m['ode']}.\n"
                f"The answer is an explicit expression in x and {consts}.")

    def score_answer(self, answer, entry):
        return score_inverse(answer, entry)
