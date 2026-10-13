"""Name the one minimal set of hypotheses that implies a conclusion, over several interpreted theories.

Variables are typed: numbers in ℕ ⊂ ℤ ⊂ ℝ ⊂ ℂ (mixed through casts `↑`), elements `i : Fin u`, sets
`S : Set (Fin u)`, maps `f : Fin u → Fin u`, and arrows `p : Fin 3 → Fin 2` between several finite
objects (a concrete category: composites, `id`, injective/surjective as mono/epi; some instances are pure
diagrams). Hypotheses and the conclusion are random well-typed atoms over that signature, so the
theories meet inside one statement (`↑(f '' S).ncard + x ^ 2 ≤ 3`). Every symbol is interpreted, and
implication is decided exactly by z3: integers and real polynomials natively, ℂ as pairs of reals, and
the finite theories unrolled over `Fin u`. The gold set is checked to be the only minimal one; instances
where z3 answers `unknown` are dropped. A theory is a sort plus entries in `_gen_*`, `_Z3` and `_show`.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, edict, stochastic_rounding as sround

NUM = ["ℕ", "ℤ", "ℝ", "ℂ"]
SORTS = NUM + ["Fin", "Set", "Fun", "Arr"]
NAMES = {"ℕ": "nmk", "ℤ": "abc", "ℝ": "xyt", "ℂ": "zwv", "Fin": "ijl", "Set": "STA", "Fun": "fgh", "Arr": "pqrsφψ"}
MAP_PREDS = ("Injective", "¬Injective", "Surjective", "¬Surjective", "Bijective")
_RLIMIT = 2_000_000


@dataclass
class MathMinimalPremisesConfig(Config):
    n_vars: int = 3
    n_hyps: int = 4
    min_gold: int = 2
    depth: int = 1
    fin_size: int = 4
    p_false: float = 0.3
    p_diagram: float = 0.3
    n_candidates: int = 8

    def apply_difficulty(self, level):
        self.n_vars = 3 + sround(0.3 * level)
        self.n_hyps = 4 + sround(0.5 * level)
        self.min_gold = 2 + sround(0.2 * level)
        self.depth = 1 + sround(0.2 * level)
        self.fin_size = 4 + sround(0.3 * level)


class _Unknown(Exception):
    pass


# ---------- random well-typed terms ----------

def _vars(ctx, *sorts):
    return [v for v, s in ctx["types"].items() if s.split(":")[0] in sorts]


def _arr_type(t, types):
    """(dom, cod) sizes of an arrow term; arrows are typed `Fin p → Fin q`, sorts written `Arr:p:q`."""
    if t[0] == "var":
        return tuple(map(int, types[t[1]].split(":")[1:]))
    if t[0] == "id":
        return (t[1], t[1])
    return (_arr_type(t[2], types)[0], _arr_type(t[1], types)[1])


def _gen_arr(ctx, p, q, d, allow_id=True):
    """A random typed composite `Fin p → Fin q` of arrow variables (or id), or None."""
    arrs = [(v, _arr_type(("var", v), ctx["types"])) for v in _vars(ctx, "Arr")]
    opts = [("var", v) for v, ty in arrs if ty == (p, q)]
    if d > 0:
        for v, (a, b) in arrs:
            rest = _gen_arr(ctx, b, q, d - 1, allow_id=False) if a == p else None
            if rest:
                opts.append(("c∘", rest, ("var", v)))
    if allow_id and p == q and random.random() < 0.3:
        opts.append(("id", p))
    return random.choice(opts) if opts else None


def _has_fin(ctx):
    return bool(_vars(ctx, "Fin", "Set", "Fun"))


def _num_sort(t, types):
    if t[0] == "var":
        return types[t[1]]
    if t[0] in ("+", "*", "^"):
        return max((_num_sort(a, types) for a in t[1:] if isinstance(a, tuple)), key=NUM.index)
    return "ℕ"  # literals, card, Fin values


def _num_leaf(ctx, d):
    """A number-valued factor: a numeric variable, a cardinality, or the value of an element of Fin u."""
    opts = [("var", v) for v in _vars(ctx, *NUM)] + ["card"] * bool(_vars(ctx, "Set")) + ["val"] * bool(_vars(ctx, "Fin", "Fun"))
    pick = random.choice(opts)
    if pick == "card":
        return ("card", _gen_set(ctx, d - 1))
    if pick == "val":
        e = _gen_elem(ctx, d - 1)
        if e[0] == "fin":  # a literal's value is just a number; use a variable element instead
            e = ("app", _gen_fun(ctx, 0), e) if _vars(ctx, "Fun") else ("var", random.choice(_vars(ctx, "Fin")))
        return ("val", e)
    return pick


def _gen_poly(ctx, d):
    """2-3 random monomials (merged, zero ones dropped) as [(coefficient, [factor, ...]), ...]."""
    monos = {}
    for _ in range(random.randint(2, 3)):
        fs = [] if random.random() < 0.3 else sorted((_num_leaf(ctx, d) for _ in range(random.choice([1, 1, 2]))), key=repr)
        c, _ = monos.get(repr(fs), (0, fs))
        monos[repr(fs)] = (c + random.choice([-3, -2, -1, 1, 1, 2, 3]), fs)
    return [(c, fs) for c, fs in monos.values() if c]


def _mono_tree(c, fs):
    parts = []
    for f in fs:
        if parts and parts[-1][0] == f:
            parts[-1][1] += 1
        else:
            parts.append([f, 1])
    trees = [f if k == 1 else ("^", f, k) for f, k in parts] or [("lit", c)]
    if fs and c != 1:
        trees.insert(0, ("lit", c))
    out = trees[0]
    for t in trees[1:]:
        out = ("*", out, t)
    return out


def _sum_tree(terms):
    trees = [_mono_tree(c, fs) for c, fs in terms] or [("lit", 0)]
    out = trees[0]
    for t in trees[1:]:
        out = ("+", out, t)
    return out


def _gen_elem(ctx, d):
    if d > 0 and _vars(ctx, "Fun") and random.random() < 0.5:
        return ("app", _gen_fun(ctx, d - 1), _gen_elem(ctx, d - 1))
    vs = _vars(ctx, "Fin")
    return ("var", random.choice(vs)) if vs and random.random() < 0.75 else ("fin", random.randrange(ctx["u"]))


def _gen_fun(ctx, d):
    fs = _vars(ctx, "Fun")
    if d > 0 and len(fs) > 1 and random.random() < 0.3:
        return ("∘", _gen_fun(ctx, d - 1), _gen_fun(ctx, d - 1))
    return ("var", random.choice(fs))


def _gen_set(ctx, d):
    ss = _vars(ctx, "Set")
    if d <= 0 or random.random() < 0.4:
        return ("var", random.choice(ss))
    ops = ["∪", "∩", "\\", "ᶜ"] + (["''", "⁻¹'"] if _vars(ctx, "Fun") else [])
    op = random.choice(ops)
    if op == "ᶜ":
        return ("ᶜ", _gen_set(ctx, d - 1))
    if op in ("''", "⁻¹'"):
        return (op, _gen_fun(ctx, 0), _gen_set(ctx, d - 1))
    return (op, _gen_set(ctx, d - 1), _gen_set(ctx, 0))


def _gen_atom(ctx):
    fams = []
    if _vars(ctx, *NUM) or _has_fin(ctx):
        fams += ["num"] * 2
    if _vars(ctx, "Fin", "Fun"):
        fams.append("elem")
    if _vars(ctx, "Set"):
        fams += ["set", "set"]
    if _vars(ctx, "Fun"):
        fams.append("fun")
    if _vars(ctx, "Arr"):
        fams += ["arr", "arr"]
    fam, d = random.choice(fams), ctx["depth"]
    if fam == "arr":
        v = random.choice(_vars(ctx, "Arr"))
        p, q = _arr_type(("var", v), ctx["types"])
        t1 = ("var", v)
        for _ in range(random.choice([0, 1, 1, 2])):
            nxt = [w for w in _vars(ctx, "Arr") if _arr_type(("var", w), ctx["types"])[0] == q]
            if nxt:
                w = random.choice(nxt)
                t1, q = ("c∘", ("var", w), t1), _arr_type(("var", w), ctx["types"])[1]
        if random.random() < 0.35:
            return (random.choice(MAP_PREDS), t1)
        t2 = _gen_arr(ctx, p, q, d + 1)
        return (random.choice(["=", "=", "≠"]), t1, t2) if t2 and t2 != t1 else ("lit", 0)
    if fam == "num":
        terms = _gen_poly(ctx, d)
        if not any(fs for _, fs in terms):
            return ("lit", 0)  # rejected by _good
        T = max((_num_sort(f, ctx["types"]) for _, fs in terms for f in fs), key=NUM.index)
        rel = random.choice(["=", "≠"] + (["≤", "<"] if T != "ℂ" else []) + (["∣"] if T in "ℕℤ" else []))
        if rel == "∣":
            return ("∣", ("lit", random.randint(2, 5)), _sum_tree([(abs(c), fs) for c, fs in terms]))
        lhs, rhs = _sum_tree([(c, fs) for c, fs in terms if c > 0]), _sum_tree([(-c, fs) for c, fs in terms if c < 0])
        return (rel, lhs, rhs) if random.random() < 0.5 or rel in "=≠" else (rel, rhs, lhs)
    if fam == "elem":
        return (random.choice(["=", "≠"]), _gen_elem(ctx, d), _gen_elem(ctx, d - 1))
    if fam == "set":
        if random.random() < 0.4:
            return (random.choice(["∈", "∉"]), _gen_elem(ctx, d - 1), _gen_set(ctx, d))
        return (random.choice(["⊆", "⊆", "=", "≠"]), _gen_set(ctx, d), _gen_set(ctx, d - 1))
    if random.random() < 0.6:
        return (random.choice(MAP_PREDS), _gen_fun(ctx, d))
    return (random.choice(["=", "≠"]), _gen_fun(ctx, d), _gen_fun(ctx, d - 1))


def _mentions_var(t):
    return isinstance(t, tuple) and (t[0] == "var" or any(_mentions_var(a) for a in t[1:]))


def _clean(t):
    """No identical operands (`S \\ S`, `f = f`) and no `+ 0`, `* 0`, `* 1`, `0 ^ 2`, `1 ^ 2`."""
    if not isinstance(t, tuple) or t[0] in ("var", "lit", "fin", "id"):
        return True
    args = [a for a in t[1:] if isinstance(a, tuple)]
    if len(args) == 2 and args[0] == args[1] and t[0] not in ("+", "*", "∘", "c∘"):
        return False
    if t[0] == "c∘" and any(a[0] == "id" for a in args):
        return False
    if t[0] in ("+", "*", "^") and any(a == ("lit", 0) or (t[0] != "+" and a == ("lit", 1)) for a in args):
        return False
    return all(map(_clean, args))


def _good(t):
    return _mentions_var(t) and _clean(t)


# ---------- z3 semantics ----------

def _kind(t, types):
    """Sort family of a term: a numeric sort, or Fin / Set / Fun."""
    h = t[0]
    if h == "var":
        return types[t[1]].split(":")[0]
    if h in ("c∘", "id"):
        return "Arr"
    if h in ("app", "fin"):
        return "Fin"
    if h in ("∘",):
        return "Fun"
    if h in ("∪", "∩", "\\", "ᶜ", "''", "⁻¹'"):
        return "Set"
    return _num_sort(t, types)


class _Z3:
    def __init__(self, types, u):
        import z3
        self.z3, self.types, self.u, self.side = z3, types, u, []
        self.env = {}
        for v, s in types.items():
            if s in ("ℕ", "ℤ"):
                self.env[v] = z3.Int(v)
                if s == "ℕ":
                    self.side.append(self.env[v] >= 0)
            elif s == "ℝ":
                self.env[v] = z3.Real(v)
            elif s == "ℂ":
                self.env[v] = (z3.Real(v + ".re"), z3.Real(v + ".im"))
            elif s == "Fin":
                self.env[v] = z3.Int(v)
                self.side += [self.env[v] >= 0, self.env[v] < u]
            elif s == "Set":
                self.env[v] = [z3.Bool(f"{v}.{k}") for k in range(u)]
            elif s.startswith("Arr"):
                p, q = map(int, s.split(":")[1:])
                self.env[v] = [z3.Int(f"{v}.{k}") for k in range(p)]
                self.side += [c for x in self.env[v] for c in (x >= 0, x < q)]
            else:
                self.env[v] = [z3.Int(f"{v}.{k}") for k in range(u)]
                self.side += [c for x in self.env[v] for c in (x >= 0, x < u)]

    def cast(self, x, have, T):
        z3 = self.z3
        if T == "ℂ":
            return x if have == "ℂ" else (z3.ToReal(x) if have in "ℕℤ" else x, z3.RealVal(0))
        return z3.ToReal(x) if T == "ℝ" and have in "ℕℤ" else x

    def num(self, t, T):
        z3, h = self.z3, t[0]
        if h == "var":
            return self.cast(self.env[t[1]], self.types[t[1]], T)
        if h == "lit":
            return self.cast(z3.IntVal(t[1]), "ℕ", T)
        if h == "card":
            return self.cast(z3.Sum([z3.If(b, 1, 0) for b in self.set(t[1])]), "ℕ", T)
        if h == "val":
            return self.cast(self.elem(t[1]), "ℕ", T)
        mul = (lambda a, b: a * b) if T != "ℂ" else (lambda a, b: (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]))
        a = self.num(t[1], T)
        if h == "^":
            out = a
            for _ in range(t[2] - 1):
                out = mul(out, a)
            return out
        b = self.num(t[2], T)
        if h == "*":
            return mul(a, b)
        return a + b if T != "ℂ" else (a[0] + b[0], a[1] + b[1])

    def apply(self, F, e):
        z3 = self.z3
        out = F[-1]
        for k in range(len(F) - 2, -1, -1):
            out = z3.If(e == k, F[k], out)
        return out

    def elem(self, t):
        if t[0] == "var":
            return self.env[t[1]]
        if t[0] == "fin":
            return self.z3.IntVal(t[1])
        return self.apply(self.fun(t[1]), self.elem(t[2]))

    def fun(self, t):
        if t[0] == "var":
            return self.env[t[1]]
        F, G = self.fun(t[1]), self.fun(t[2])
        return [self.apply(F, g) for g in G]

    def arr(self, t):
        if t[0] == "var":
            return self.env[t[1]]
        if t[0] == "id":
            return [self.z3.IntVal(k) for k in range(t[1])]
        G = self.arr(t[1])
        return [self.apply(G, x) for x in self.arr(t[2])]

    def member(self, e, S):
        return self.z3.Or([self.z3.And(e == k, S[k]) for k in range(self.u)])

    def set(self, t):
        z3, h = self.z3, t[0]
        if h == "var":
            return self.env[t[1]]
        if h == "ᶜ":
            return [z3.Not(b) for b in self.set(t[1])]
        if h == "''":
            F, S = self.fun(t[1]), self.set(t[2])
            return [z3.Or([z3.And(S[k], F[k] == y) for k in range(self.u)]) for y in range(self.u)]
        if h == "⁻¹'":
            F, S = self.fun(t[1]), self.set(t[2])
            return [self.member(F[k], S) for k in range(self.u)]
        A, B = self.set(t[1]), self.set(t[2])
        f = {"∪": z3.Or, "∩": z3.And, "\\": lambda a, b: z3.And(a, z3.Not(b))}[h]
        return [f(a, b) for a, b in zip(A, B)]

    def atom(self, t):
        z3, h = self.z3, t[0]
        if h in MAP_PREDS:
            arrow = _kind(t[1], self.types) == "Arr"
            F, cod = (self.arr(t[1]), _arr_type(t[1], self.types)[1]) if arrow else (self.fun(t[1]), self.u)
            inj = z3.Distinct(F) if len(F) > 1 else z3.BoolVal(True)
            surj = z3.And([z3.Or([x == y for x in F]) for y in range(cod)])
            p = z3.And(inj, surj) if h == "Bijective" else inj if "Inj" in h else surj
            return z3.Not(p) if h[0] == "¬" else p
        if h in ("∈", "∉"):
            p = self.member(self.elem(t[1]), self.set(t[2]))
            return p if h == "∈" else z3.Not(p)
        if h == "∣":
            return self.num(t[2], "ℤ") % t[1][1] == 0
        if h == "⊆":
            return z3.And([z3.Implies(a, b) for a, b in zip(self.set(t[1]), self.set(t[2]))])
        k = _kind(t[1], self.types)
        if k in NUM:
            T = max(k, _num_sort(t[2], self.types), key=NUM.index)
            a, b = self.num(t[1], T), self.num(t[2], T)
            if T == "ℂ":
                eq = z3.And(a[0] == b[0], a[1] == b[1])
            else:
                eq = a == b
                if h in "≤<":
                    return a <= b if h == "≤" else a < b
        else:
            ev = {"Fin": self.elem, "Set": self.set, "Fun": self.fun, "Arr": self.arr}[k]
            a, b = ev(t[1]), ev(t[2])
            eq = a == b if k == "Fin" else z3.And([x == y for x, y in zip(a, b)])
        return eq if h == "=" else z3.Not(eq)


class _Prover:
    """One incremental z3 solver for fixed hypotheses and candidate conclusions (None means False);
    `entails(idx, k)` asks whether the hypotheses numbered `idx` imply conclusion `k`."""

    def __init__(self, hyps, concls, types, u):
        E = _Z3(types, u)
        self.z3, self.s = E.z3, E.z3.Solver()
        self.s.set("rlimit", _RLIMIT)  # deterministic budget; nonlinear arithmetic can overrun it, hence the timeout
        self.s.set("timeout", 500)
        self.s.add(E.side)
        self.lits = [E.z3.Bool(f"_h{i}") for i in range(len(hyps))]
        self.s.add([E.z3.Implies(l, E.atom(h)) for l, h in zip(self.lits, hyps)])
        self.goals = []
        for k, c in enumerate(concls):
            self.goals.append([] if c is None else [E.z3.Bool(f"_c{k}")])
            if c is not None:
                self.s.add(E.z3.Implies(self.goals[-1][0], E.z3.Not(E.atom(c))))

    def entails(self, idx, k=0):
        try:
            res = self.s.check([self.lits[i] for i in idx] + self.goals[k])
        except self.z3.Z3Exception:  # "canceled" when the timeout hits during an incremental check
            raise _Unknown
        if res == self.z3.unknown:
            raise _Unknown
        return res == self.z3.unsat

    def minimal(self, idx, k=0, at_least=0):
        """A minimal entailing subset, shrunk from z3's unsat core; [] early if the core is smaller than `at_least`."""
        assert self.entails(idx, k)
        gold = sorted(int(str(c)[2:]) for c in self.s.unsat_core() if str(c).startswith("_h"))
        if len(gold) < at_least:
            return []
        for i in list(gold):
            if self.entails([j for j in gold if j != i], k):
                gold.remove(i)
        return gold


# ---------- rendering ----------

_PREC = {"+": 65, "*": 70, "^": 75}


def _paren(s, cond):
    return f"({s})" if cond else s


def _show(t, types, T=None, prec=0):
    h = t[0]
    if h == "var":
        return ("↑" if T and types[t[1]] != T and types[t[1]] in NUM else "") + t[1]
    if h in ("lit", "fin"):
        return str(t[1])
    if h == "card":
        return ("↑" if T and T != "ℕ" else "") + _paren(_show(t[1], types), t[1][0] != "var") + ".ncard"
    if h == "val":
        return "↑" + _paren(_show(t[1], types), t[1][0] not in ("var", "fin"))
    if h in _PREC:
        p = _PREC[h]
        right = str(t[2]) if h == "^" else _show(t[2], types, T, p + 1)
        return _paren(f"{_show(t[1], types, T, p + (h == '^'))} {h} {right}", prec > p)
    if h == "app":
        f = _paren(_show(t[1], types), t[1][0] != "var")
        return _paren(f"{f} {_paren(_show(t[2], types), t[2][0] == 'app')}", prec > 0)
    if h == "ᶜ":
        return _paren(_show(t[1], types), t[1][0] != "var") + "ᶜ"
    if h == "id":
        return "id"
    if h == "c∘":  # composition is associative: no inner parentheses
        return _paren(f"{_show(t[1], types)} ∘ {_show(t[2], types)}", prec > 0)
    sub = lambda x: _paren(_show(x, types), x[0] not in ("var", "ᶜ"))
    return _paren(f"{sub(t[1])} {h} {sub(t[2])}", prec > 0)


def render_atom(t, types):
    if t is None:
        return "False"
    h = t[0]
    if h in MAP_PREDS:
        return f"{h} {_paren(_show(t[1], types), t[1][0] != 'var')}"
    T = None
    if h == "∣":
        T = _num_sort(t[2], types)
    elif _kind(t[1], types) in NUM:
        T = max(_num_sort(t[1], types), _num_sort(t[2], types), key=NUM.index)
    return f"{_show(t[1], types, T)} {h} {_show(t[2], types, T)}"


# ---------- instance search ----------

def _var_set(t):
    if not isinstance(t, tuple):
        return set()
    return {t[1]} if t[0] == "var" else set().union(*map(_var_set, t[1:]))


def _atom_over(ctx, vs):
    """A clean atom mentioning every variable in `vs` and nothing else (None if the sorts don't meet)."""
    sub = dict(ctx, types={v: ctx["types"][v] for v in vs})
    for _ in range(10):
        t = _gen_atom(sub)
        if _var_set(t) == set(vs) and _clean(t):
            return t
    return None


_NEG = {"=": "≠", "∈": "∉", "Injective": "¬Injective", "Surjective": "¬Surjective"}
_NEG.update({v: k for k, v in _NEG.items()})


def _negation(t):
    return (_NEG[t[0]],) + t[1:] if t[0] in _NEG else None


def _solve(cfg, types, hyps, concl_gen):
    """(types, hyps, conclusion, gold) if some candidate conclusion has a unique minimal premise set of the
    wanted size, else None. Inconsistent hypotheses get the conclusion False."""
    u, every = cfg.fin_size, range(len(hyps))
    try:
        if _Prover(hyps, [None], types, u).entails(every):
            if random.random() > cfg.p_false:
                return None
            cands = [None]
        else:
            cands = [c for c in (concl_gen() for _ in range(cfg.n_candidates)) if c and _good(c) and c not in hyps]
        P = _Prover(hyps, cands, types, u)
        for k, concl in enumerate(cands):
            if not P.entails(every, k) or (concl is not None and P.entails([], k)):
                continue
            gold = P.minimal(every, k, cfg.min_gold)
            if not cfg.min_gold <= len(gold) < len(hyps):
                continue
            if any(P.entails([j for j in every if j != i], k) for i in gold):
                continue
            if any(_negation(hyps[i]) == hyps[j] for i in gold for j in gold):
                continue  # `a = b` with `a ≠ b` is not a proof worth asking for
            return types, hyps, concl, gold
    except _Unknown:
        pass
    return None


def _diagram_instance(cfg):
    """All variables are arrows between 2-3 objects `Fin p` (sizes 1-4): a concrete category of finite sets."""
    objects = random.sample(range(1, 5), random.choice([2, 3]))
    types = {}
    for v in NAMES["Arr"][:min(len(NAMES["Arr"]), cfg.n_vars + 1)]:
        types[v] = f"Arr:{random.choice(objects)}:{random.choice(objects)}"
    ctx = {"types": types, "u": cfg.fin_size, "depth": cfg.depth}
    hyps = []
    for _ in range(10 * cfg.n_hyps):
        t = _gen_atom(ctx)
        if _good(t) and t not in hyps:
            hyps.append(t)
        if len(hyps) == cfg.n_hyps:
            return _solve(cfg, types, hyps, lambda: _gen_atom(ctx))
    return None


def _generate(cfg):
    """The core links a path of variables v0 - v1 - ... - vk, one hypothesis per edge, and a conclusion
    candidate links v0 to vk, so the proof has to chain; distractors reuse the same variables."""
    for _ in range(3000):
        if random.random() < cfg.p_diagram:
            got = _diagram_instance(cfg)
            if got:
                return got
            continue
        sorts = random.choices(SORTS, weights=[1, 1, 1, 1, 1, 2, 1.5, 1], k=cfg.n_vars)
        if sorts.count("Arr") == 1:  # one arrow is no diagram
            sorts.append("Arr")
        objects = random.sample(range(1, 5), random.choice([2, 3]))
        types, used = {}, {}
        for s in sorted(sorts, key=SORTS.index):
            if used.get(s, 0) < len(NAMES[s]):
                types[NAMES[s][used.get(s, 0)]] = s if s != "Arr" else f"Arr:{random.choice(objects)}:{random.choice(objects)}"
            used[s] = used.get(s, 0) + 1
        ctx, names = {"types": types, "u": cfg.fin_size, "depth": cfg.depth}, list(types)
        path = [random.choice(names)]
        for _ in range(cfg.min_gold - 1):
            path.append(random.choice([v for v in names if v != path[-1]] or names))
        core = [_atom_over(ctx, sorted({x, y})) for x, y in zip(path, path[1:])]
        core.append(_atom_over(ctx, [random.choice(names)]))
        extra = [_atom_over(ctx, random.sample(names, min(2, len(names)))) for _ in range(cfg.n_hyps - len(core))]
        hyps = core + extra
        if None in hyps or len({repr(h) for h in hyps}) < len(hyps):
            continue
        random.shuffle(hyps)
        ends = sorted({path[0], path[-1]})
        got = _solve(cfg, types, hyps, lambda: _atom_over(ctx, ends))
        if got:
            return got
    raise RuntimeError("math_minimal_premises: no instance found")


def _declare(types, u):
    groups = {}
    for v, s in types.items():
        groups.setdefault(s, []).append(v)
    full = {"Fin": f"Fin {u}", "Set": f"Set (Fin {u})", "Fun": f"Fin {u} → Fin {u}"}
    show = lambda s: "Fin {} → Fin {}".format(*s.split(":")[1:]) if s.startswith("Arr") else full.get(s, s)
    return ", ".join(f"{' '.join(vs)} : {show(s)}" for s, vs in groups.items())


class MathMinimalPremises(DevTask):
    summary = ("Given typed variables (ℕ ⊂ ℤ ⊂ ℝ ⊂ ℂ with casts, Fin u, sets and maps on Fin u, arrows "
               "Fin p → Fin q), numbered hypotheses mixing arithmetic, divisibility, set algebra, images, "
               "cardinality, injectivity/surjectivity and commuting diagrams of composites, and a conclusion "
               "(possibly False), name the unique minimal set of hypotheses that implies it; decided by z3.")
    config_cls = MathMinimalPremisesConfig
    task_version = 2  # prompt: "implies" (was "proves"), and `∘` / `id` explained for arrow instances

    def generate_entry(self):
        cfg = self.config
        types, hyps, concl, gold = _generate(cfg)
        meta = edict(variables=_declare(types, cfg.fin_size), hypotheses=[render_atom(h, types) for h in hyps],
                     conclusion=render_atom(concl, types))
        return Entry(metadata=meta, answer=", ".join(str(i + 1) for i in gold))

    def render_prompt(self, m):
        hyps = "\n".join(f"{i + 1}. {h}" for i, h in enumerate(m.hypotheses))
        return (f"Variables: {m.variables}\nHypotheses:\n{hyps}\nConclusion: {m.conclusion}\n\n"
                "Notation is Lean/Mathlib: `↑` casts to the type of the surrounding expression, "
                "`f '' S` is the image and `f ⁻¹' S` the preimage of S, `Sᶜ` the complement in Fin, "
                "`S.ncard` the number of elements, `g ∘ f` the composite (f first) and `id` the identity. "
                "Exactly one set of hypotheses implies the conclusion "
                "with every member needed. List its numbers in increasing order, comma-separated (e.g. 1, 3).")

    def score_answer(self, answer, entry):
        return float(_parse(answer) == _parse(entry.answer))


def _parse(s):
    try:
        return sorted({int(t) for t in str(s).strip().strip("{}[]().").replace(" ", "").split(",") if t})
    except ValueError:
        return None
