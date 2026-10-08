"""Planted-witness mathematics: find unknowns W with E_i(W) = y_i, where each E_i is a random typed term.

One generic shape instead of a list of problem types. A witness W* is sampled by type, a system of
random operator terms over the unknowns is sampled from a typed grammar, and y_i = E_i(W*). The
task is to find *any* W satisfying the system; the only checker plugs the candidate back in.

What is chosen by hand (and only this): the types, the operator grammar below, and generic
filters. No problem type is named anywhere; integration, antidifferences, factorizations,
functional equations, systems, ... are whatever terms the grammar happens to produce.
Semantics are sympy's.
"""
import random
import re
from dataclasses import dataclass

import sympy as sp

from reasoning_core.runtime import timeout_retry
from reasoning_core.template import Config, Entry, Task, stochastic_rounding
from reasoning_core.tasks.dev.math_inverse import normalize, random_expr, show, _num, _close, _SAFE, _FUNCS, _TRANSFORMS
from sympy.parsing.sympy_parser import parse_expr

x, n = sp.symbols("x n")
VAR = {"function": x, "polynomial": x, "sequence": n, "number": None}
KINDS = ["number", "polynomial", "sequence"]  # functions: no finite reduction, so uniqueness is not certifiable
NAMES = {"function": ["f", "g"], "polynomial": ["p", "q"], "sequence": ["a", "b"], "number": ["X", "Y"]}


# ---------------------------------------------------------------- typed grammar
# A term is a nested tuple:
#   ("u", i, arg)       unknown i at argument arg (arg: None for numbers, else an expression of the variable)
#   ("uu", i, j)        unknown i composed with unknown j (functions only)
#   ("D", t)            derivative (function-valued types only)
#   ("add", t, s) | ("mul", t, s) | ("scale", c, t) | ("pow", t, k)
#   ("known+", t, e) | ("known*", t, e) | ("apply", name, t)   with e a known expression

def _known(kind):
    v = VAR[kind]
    if kind == "number":
        return sp.Integer(random.choice([2, 3, 5, -2, -3]))
    if kind == "sequence":
        return random.choice([n, n ** 2, 2 ** n, sp.Integer(random.randint(2, 5))])
    if kind == "polynomial":
        return sp.expand(sum(random.randint(-3, 3) * v ** j for j in range(random.randint(1, 3))) + v)
    return random.choice([random_expr(random.randint(0, 1)), v + random.randint(1, 3), v ** 2])


def _args(kind):
    v = VAR[kind]
    if kind == "sequence":
        return [n, n + 1, n + 2, 2 * n]
    return [v, v + 1, 2 * v, -v, v ** 2] if kind == "function" else [v, v + 1, -v, 2 * v]


def random_term(size, kind, k):
    if size <= 0:
        i = random.randrange(k)
        if kind == "function" and random.random() < 0.1:
            return ("uu", i, random.randrange(k))
        if kind in ("polynomial", "sequence") and random.random() < 0.2:  # evaluation at a point: p(1), a(0)
            return ("u", i, sp.Integer(random.choice([0, 1, 2] if kind == "sequence" else [0, 1, -1, 2])))
        return ("u", i, None if kind == "number" else random.choice(_args(kind)))
    ops = ["add", "mul", "scale", "pow", "known+", "known*"]
    ops += {"function": ["D", "D", "apply"], "polynomial": ["D"], "sequence": [], "number": ["apply"]}[kind]
    op = random.choice(ops)
    sub = lambda s=size - 1: random_term(s, kind, k)
    if op == "D":
        return ("D", sub())
    if op in ("add", "mul"):
        return (op, sub(), random_term(random.randint(0, size - 1), kind, k))
    if op == "scale":
        return ("scale", random.choice([2, 3, -1, -2, sp.Rational(1, 2)]), sub())
    if op == "pow":
        return ("pow", sub(), random.choice([2, 2, 3]))
    if op == "apply":
        return ("apply", random.choice(["exp", "log", "sin", "sqrt"]), sub())
    return (op, sub(), _known(kind))


def evaluate(t, W, kind, leaf=None, at=None):
    """Term value when unknown i is the expression W[i] (in the type's variable).

    With `leaf` and `at` (sequences), the term is instead instantiated at n = at, and leaf(i, arg)
    stands for unknown i at argument arg, so no symbolic substitution is needed.
    """
    v, op = VAR[kind], t[0]
    ev = lambda s: evaluate(s, W, kind, leaf, at)
    if op == "u":
        if leaf is not None:
            return leaf(t[1], t[2])
        return W[t[1]] if t[2] is None or t[2] == v else W[t[1]].subs(v, t[2])
    if op == "uu":
        return W[t[1]].subs(v, W[t[2]])
    if op == "D":
        return sp.diff(ev(t[1]), v)
    if op == "add":
        return ev(t[1]) + ev(t[2])
    if op == "mul":
        return ev(t[1]) * ev(t[2])
    if op == "scale":
        return t[1] * ev(t[2])
    if op == "pow":
        return ev(t[1]) ** t[2]
    known = t[2] if at is None or not isinstance(t[2], sp.Basic) else t[2].xreplace({n: at})
    if op == "known+":
        return ev(t[1]) + known
    if op == "known*":
        return ev(t[1]) * known
    if op == "apply":
        return _APPLY[t[1]](ev(t[2]))
    raise ValueError(op)


_APPLY = {"exp": sp.exp, "log": sp.log, "sin": sp.sin, "sqrt": sp.sqrt}


def render(t, kind):
    return _render(t, kind)[0]


def _atom(e):
    """Known constant or expression as text, with its precedence (3 atom, 2 power, 1 product, 0 sum)."""
    e = sp.sympify(e)
    txt = show(e)
    if e.is_Add or (e.is_Number and e < 0) or e.is_Rational and not e.is_Integer:
        return txt, 0 if e.is_Add or e < 0 else 1
    return txt, 1 if e.is_Mul else 3


def _render(t, kind):
    """Text and precedence of a term; parenthesise only where precedence requires it."""
    names, v, op = NAMES[kind], VAR[kind], t[0]
    par = lambda r, p: r[0] if r[1] >= p else f"({r[0]})"
    if op == "u":
        return (names[t[1]] if kind == "number" else f"{names[t[1]]}({show(t[2])})"), 3
    if op == "uu":
        return f"{names[t[1]]}({names[t[2]]}({v}))", 3
    if op == "D":
        inner, k = t[1], 1
        while inner[0] == "D":
            inner, k = inner[1], k + 1
        if inner[0] == "u" and inner[2] == v:
            return f"{names[inner[1]]}{chr(39) * k}({v})", 3
        order = f"^{k}" if k > 1 else ""
        return f"d{order}/d{v}{order}[{render(inner, kind)}]", 3
    if op in ("add", "known+"):
        b = _render(t[2], kind) if op == "add" else _atom(t[2])
        rb = f"- {par((b[0][1:], b[1]), 1)}" if b[0].startswith("-") and b[1] >= 1 else f"+ {b[0]}"
        return f"{_render(t[1], kind)[0]} {rb}", 0
    if op in ("mul", "known*", "scale"):
        a, b = (_atom(t[1]), _render(t[2], kind)) if op == "scale" else (_render(t[1], kind), _render(t[2], kind) if op == "mul" else _atom(t[2]))
        if op == "known*" and b[1] == 3 and not b[0][0].isalpha() or op == "known*" and b[1] < 3:
            a, b = b, a  # constants in front: 2*f(x), (x + 1)*f(x)
        if a[0] == "-1":
            return f"-{par(b, 2)}", 0
        return f"{par(a, 1)}*{par(b, 2)}", 1
    if op == "pow":
        return f"{par(_render(t[1], kind), 3)}^{t[2]}", 2
    if op == "apply":
        return f"{t[1]}({render(t[2], kind)})", 3
    raise ValueError(op)


def encode(t):
    """JSON-safe form: strings stay, sympy numbers/expressions become srepr strings tagged with '$'."""
    if isinstance(t, tuple):
        return [encode(c) for c in t]
    if isinstance(t, (str, int)) or t is None:
        return t
    return "$" + sp.srepr(t)


def decode(t):
    if isinstance(t, list):
        return tuple(decode(c) for c in t)
    return sp.sympify(t[1:]) if isinstance(t, str) and t.startswith("$") else t


def _unknowns(t):
    if t[0] == "u":
        return {t[1]}
    if t[0] == "uu":
        return {t[1], t[2]}
    return set().union(*(_unknowns(c) for c in t[1:] if isinstance(c, tuple)))


# ---------------------------------------------------------------- witnesses and generic filters

def sample_witness(kind, size):
    v = VAR[kind]
    for _ in range(50):
        if kind == "number":
            w = sp.Rational(random.randint(-9, 9), random.choice([1, 1, 2, 3]))
        elif kind == "polynomial":
            w = sp.expand(sum(random.randint(-4, 4) * v ** j for j in range(random.randint(2, 2 + size // 2))))
        elif kind == "sequence":
            w = sp.expand(sum(random.choice([1, 2, -1, 3]) * random.choice([n, n ** 2, 2 ** n, 3 ** n, (-1) ** n, n * 2 ** n])
                              for _ in range(random.randint(1, 1 + size // 3))) + random.randint(-3, 3))
        else:
            w = random_expr(max(1, size // 2))
        if kind == "number" or v in w.free_symbols:  # a function-valued witness must actually vary
            return w
    return None


def _trivial(kind):
    v = VAR[kind]
    return [sp.Integer(0), sp.Integer(1), sp.Integer(-1)] + ([] if v is None else [v, v + 1, -v, 2 * v])


def _holds(system, W, kind):
    """Does assignment W satisfy every equation? Exact when possible, else numeric at random points."""
    v = VAR[kind]
    for t, y in system:
        diff = evaluate(t, W, kind) - y
        if kind in ("number", "polynomial"):
            try:
                if sp.nsimplify(sp.expand(diff)) != 0 and abs(complex(sp.N(diff.subs(v, sp.Rational(7, 5)) if v else diff))) > 1e-9:
                    return False
            except (TypeError, ValueError):
                return False
            continue
        pts = [sp.Integer(i) for i in range(0, 7)] if kind == "sequence" else [sp.Rational(r, 17) for r in (5, 9, 13, 21, 30)]
        ok = 0
        for p in pts:
            a, b = _num(evaluate(t, W, kind), v, p), _num(y, v, p)
            if a is None and b is None:
                continue
            if not _close(a, b):
                return False
            ok += 1
        if ok < 3:
            return False
    return True


def _rhs(t, W, kind):
    y = evaluate(t, W, kind)  # expanded, so the planted structure is not printed back
    if kind == "sequence":  # (-1)^(c*n) -> (-1)^(c mod 2 * n), which expand leaves alone
        y = sp.expand(y).replace(lambda e: e.is_Pow and e.base == -1 and e.exp.as_coeff_Mul()[0].is_Integer,
                                 lambda e: (-1) ** ((e.exp.as_coeff_Mul()[0] % 2) * e.exp.as_coeff_Mul()[1]))
    return sp.expand(y) if kind != "function" else sp.expand(sp.simplify(y))


def _deg(t, degs):
    """Upper bound on the x-degree of a polynomial term when unknown i has degree degs[i]."""
    op = t[0]
    if op == "u":
        return degs[t[1]] * max(1, sp.degree(t[2], x))
    if op == "uu":
        return degs[t[1]] * degs[t[2]]
    if op == "D":
        return max(0, _deg(t[1], degs) - 1)
    if op == "add":
        return max(_deg(t[1], degs), _deg(t[2], degs))
    if op == "mul":
        return _deg(t[1], degs) + _deg(t[2], degs)
    if op == "scale":
        return _deg(t[2], degs)
    if op == "pow":
        return _deg(t[1], degs) * t[2]
    if op == "known+":
        return max(_deg(t[1], degs), sp.degree(t[2], x))
    return _deg(t[1], degs) + sp.degree(t[2], x)  # known*


def unique(terms, ys, W, kind):
    """Is W the only solution? Each type is reduced to finitely many unknowns and sympy solves the whole system.

    number: X, Y themselves. polynomial: coefficients of a degree deg(W*)+1 ansatz, so free constants,
    free parity parts or higher-degree alternatives would show up. sequence: the values a(0..M), with the
    equations instantiated at n = 0..6; a(0..4) must be pinned (a(n + 2) alone leaves a(0), a(1) free).
    """
    v, k = VAR[kind], len(W)
    if set().union(set(), *map(_unknowns, terms)) != set(range(k)):
        return False
    if kind == "number":
        U = sp.symbols(f"u0:{k}")
        eqs, targets = [evaluate(t, list(U), kind) - y for t, y in zip(terms, ys)], list(U)
        point = dict(zip(U, W))
    elif kind == "polynomial":
        U, targets, point, degs = [], [], {}, []
        for i, w in enumerate(W):
            cs = sp.symbols(f"c{i}_0:{sp.degree(w, v) + 2}")
            U.append(sum(c * v ** j for j, c in enumerate(cs)))
            targets += cs
            degs.append(len(cs) - 1)
            point.update({c: w.coeff(v, j) for j, c in enumerate(cs)})
        # a polynomial identity of degree <= D holds iff it holds at D + 1 points: no symbolic expansion
        eqs = [evaluate(t, U, kind).subs(v, a) - y.subs(v, a)
               for t, y in zip(terms, ys) for a in range(-(_deg(t, degs) // 2), _deg(t, degs) - _deg(t, degs) // 2 + 1)]
    else:
        cell = lambda i, arg, m: sp.Symbol(f"s{i}_{int(arg.xreplace({n: m}))}")
        eqs = [evaluate(t, None, kind, leaf=lambda i, arg: cell(i, arg, m), at=m) - y.xreplace({n: m})
               for t, y in zip(terms, ys) for m in range(7)]
        point = {c: W[int(c.name[1])].xreplace({n: int(c.name.split("_")[1])})
                 for c in set().union(*(e.free_symbols for e in eqs))}
        targets = [sp.Symbol(f"s{i}_{m}") for i in range(k) for m in range(5)]
        if not set(targets) <= set(point):
            return False
    unknowns = sorted(point, key=str)
    # cheap exact test first: a null direction of the Jacobian at W* that moves a target means W* is not isolated
    J = sp.Matrix(eqs).jacobian(unknowns).subs(point)
    idx = [unknowns.index(c) for c in targets]
    if any(vec[i] != 0 for vec in J.nullspace() for i in idx):
        return False
    sols = sp.solve(eqs, unknowns, dict=True)
    if not sols:
        return False
    pinned = [tuple(sol.get(c) for c in targets) for sol in sols]
    return len(set(pinned)) == 1 and all(p is not None and not getattr(p, "free_symbols", None) for p in pinned[0])


@dataclass
class PlantedWitnessConfig(Config):
    term_size: float = 1.0  # operator depth of each equation, capped: deeper terms only add bloat
    witness_size: float = 1.0  # size of the hidden objects
    max_unknowns: float = 1.3

    def apply_difficulty(self, level):
        self.term_size = min(3.0, self.term_size + 0.3 * level)
        self.witness_size += 0.5 * level
        self.max_unknowns += 0.15 * level


def _equation(size, kind, W, tries=6):
    """One equation T(W*) = y, redrawn if degenerate, too long, or if the witness is readable off y."""
    for _ in range(tries):
        t = random_term(size, kind, len(W))
        y = _rhs(t, W, kind)
        l, r = render(t, kind), show(y)
        if not (y.has(sp.nan, sp.zoo, sp.oo, sp.I) or len(l) + len(r) > 250 or any(show(w) in r for w in W if not w.is_Atom)):
            return t, y
    return None


@timeout_retry(seconds=1, attempts=1)
def _timed_draw(task, *args):  # a slow draw (huge numeric checks) is rejected, not waited for
    return task._draw(*args)


class PlantedWitness(Task):
    summary = "Find the unique numbers, polynomials or sequences satisfying a system of equations built from random typed operator terms (derivatives, shifts, substitutions, compositions, products, powers) with a planted solution."
    config_cls = PlantedWitnessConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        kind = random.choice(KINDS)  # drawn once, so rejection rates do not skew the type mix
        for _ in range(300):
            try:
                out = _timed_draw(self, kind, stochastic_rounding(cfg.term_size), stochastic_rounding(cfg.witness_size),
                                  max(1, min(2, stochastic_rounding(cfg.max_unknowns))))
            except Exception:
                continue
            if out:
                return Entry(metadata=out[0], answer=out[1])
        raise RuntimeError("planted_witness: no well-posed draw after 300 attempts")

    def _draw(self, kind, size, wsize, k):
        W = [sample_witness(kind, wsize) for _ in range(k)]
        if None in W or any(w in _trivial(kind) for w in W):
            return None
        system = []
        while len(system) < k or not unique([t for t, _ in system], [y for _, y in system], W, kind):
            if len(system) == k + 2:
                return None  # planted, so extra equations never contradict: add them until the solution is unique
            eq = _equation(size, kind, W)
            if eq is None:
                return None
            system.append(eq)
        for i in reversed(range(len(system))):  # minimal: drop any equation the others already imply
            rest = system[:i] + system[i + 1:]
            if rest and unique([t for t, _ in rest], [y for _, y in rest], W, kind):
                system = rest
        if not _holds(system, W, kind):
            return None
        terms = [t for t, _ in system]
        texts = [(render(t, kind), show(y)) for t, y in system]
        names = NAMES[kind][:k]
        meta = {"kind": kind, "unknowns": names, "equations": [f"{l} = {r}" for l, r in texts],
                "terms": [encode(t) for t in terms], "rhs": [sp.srepr(y) for _, y in system]}
        answer = ", ".join(f"{nm}{'' if kind == 'number' else f'({VAR[kind]})'} = {show(w)}" for nm, w in zip(names, W))
        return meta, answer

    def render_prompt(self, m):
        kind, names = m["kind"], m["unknowns"]
        v = VAR[kind]
        what = {"number": "numbers", "function": "functions", "polynomial": "polynomials with integer coefficients",
                "sequence": "sequences"}[kind]
        unk = ", ".join(names if kind == "number" else [f"{nm}({v})" for nm in names])
        scope = {"number": "", "function": " for all x in their domain", "polynomial": " for all x",
                 "sequence": " for all integers n >= 0"}[kind]
        eqs = "\n".join(f"  {e}" for e in m["equations"])
        form = "" if kind == "number" else f" Each is an explicit closed-form expression in {v}."
        return (f"Find {what} {unk} such that{scope}:\n{eqs}\n"
                f"The solution is unique.{form} Answer as '{', '.join(f'{nm} = ...' if kind == 'number' else f'{nm}({v}) = ...' for nm in names)}'.")

    def score_answer(self, answer, entry):
        return score_witness(answer, entry)



def _parse_value(text, kind):
    v = VAR[kind]
    allowed = set(_FUNCS) | ({v.name} if v is not None else set())
    if len(text) > 400 or not _SAFE.match(text) or "__" in text or set(re.findall(r"[A-Za-z_]\w*", text)) - allowed:
        return None
    try:
        e = parse_expr(text, local_dict={**_FUNCS, **({v.name: v} if v is not None else {})}, transformations=_TRANSFORMS)
    except Exception:
        return None
    if kind == "polynomial" and not (e.is_polynomial(v) and all(c.is_integer for c in sp.Poly(e, v).coeffs())):
        return None
    return e


def score_witness(answer, entry):
    m = entry["metadata"]
    kind, names = m["kind"], m["unknowns"]
    try:
        text = normalize(answer)
        marks = {nm: list(re.finditer(rf"(?<![A-Za-z]){nm}(\(\s*[xn]\s*\))?\s*=", text)) for nm in names}
        if any(len(v) != 1 for v in marks.values()):
            return 0.0
        starts = sorted((marks[nm][0].start(), marks[nm][0].end(), nm) for nm in names)
        W = {}
        for i, (_, end, nm) in enumerate(starts):
            stop = starts[i + 1][0] if i + 1 < len(starts) else len(text)
            W[nm] = _parse_value(text[end:stop].strip().rstrip(".,; ").removesuffix("and").strip(), kind)
        if None in W.values():
            return 0.0
        W = [W[nm] for nm in names]
        terms, ys = [decode(t) for t in m["terms"]], [sp.sympify(r) for r in m["rhs"]]
        return float(_holds(list(zip(terms, ys)), W, kind))
    except Exception:
        return 0.0
