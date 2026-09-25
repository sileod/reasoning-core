import random
import re

import numpy as np
import sympy as sp

from reasoning_core.template import Config, Entry, Task

_t = sp.Symbol("t", real=True)

TASK_META = {
    "parent_source_id": None,
    "idea": "parametric_root_stability (variant 2 of 3)",
    "hypothesis": "P004",
    "changes": "new task in "
    "reasoning_core/tasks/generated/ua_global_over_greedy_r4/parametric_root_stability",
    "generation": {
        "provider_name": "albert",
        "model_name": "deepseek-v4-flash",
        "harness_name": "opencode",
        "harness_version": "1.18.32",
        "agent_name": "task-search-worker",
        "settings": {
            "variant": None,
            "requested_seed": 3577985643,
            "seed_forwarded": True,
            "temperature": None,
            "top_p": None,
            "pure": True,
            "max_steps": 56,
            "timeout_seconds": 1800,
            "sandbox": {"name": "bubblewrap", "version": "bubblewrap 0.8.0"},
        },
    },
}


def _stable_numeric(coeff_fns, tv, kind, tol=1e-7):
    tv = float(tv)
    if not np.isfinite(tv) or abs(tv) > 1e9:
        return False
    a_lead, b_lead = coeff_fns[-1]
    if abs(a_lead * tv + b_lead) < tol:
        return False
    cs = [a * tv + b for (a, b) in coeff_fns][::-1]
    roots = np.roots(np.asarray(cs, dtype=float))
    if kind == "hurwitz":
        return all(r.real < -tol for r in roots)
    return all(abs(r) < 1 - tol for r in roots)


def _critical_points(coeff_fns, kind):
    n = len(coeff_fns) - 1
    pts = set()
    for a, b in coeff_fns:
        if a != 0:
            pts.add(sp.Rational(-b, a))
    z = sp.Symbol("z")
    poly = sum((sp.Rational(a) * _t + sp.Rational(b)) * z ** k for k, (a, b) in enumerate(coeff_fns))
    if kind == "hurwitz":
        w = sp.Symbol("w", real=True)
        pw = sp.expand(poly.subs(z, sp.I * w))
        U = sp.expand(sp.re(pw))
        V = sp.expand(sp.im(pw))
        res = None if (U == 0 or V == 0) else sp.resultant(sp.Poly(U, w), sp.Poly(V, w))
    else:
        rec = sp.expand(z ** n * poly.subs(z, 1 / z))
        res = None if rec == 0 else sp.resultant(sp.Poly(poly, z), sp.Poly(rec, z))
    if res is not None:
        res = sp.factor(sp.expand(res))
        if res.has(_t):
            for r in sp.real_roots(sp.Poly(res, _t)):
                pts.add(r)
    crit = sorted(pts, key=lambda v: float(sp.N(v)))
    merged = []
    for v in crit:
        if not merged or float(sp.N(merged[-1] - v)) != 0:
            merged.append(v)
    return merged


def _build_segs(coeff_fns, kind, crit):
    n = len(crit)
    gaps = []
    if n >= 1:
        gaps.append((sp.S.NegativeInfinity, crit[0]))
        for i in range(n - 1):
            gaps.append((crit[i], crit[i + 1]))
        gaps.append((crit[n - 1], sp.S.Infinity))
    segs = []
    for lo, hi in gaps:
        if lo is sp.S.NegativeInfinity:
            mid = hi - (1 + abs(float(sp.N(hi))))
        elif hi is sp.S.Infinity:
            mid = lo + (1 + abs(float(sp.N(lo))))
        else:
            mid = (float(sp.N(lo)) + float(sp.N(hi))) / 2.0
        if _stable_numeric(coeff_fns, mid, kind):
            segs.append([lo, hi, False, False])
    return segs


def _merge(segs):
    def key(q):
        lo, hi, _, _ = q
        lk = -float("inf") if lo.is_infinite else float(sp.N(lo))
        hk = float("inf") if hi.is_infinite else float(sp.N(hi))
        return (lk, hk)

    segs = sorted(segs, key=key)
    res = []
    for s in segs:
        if not res:
            res.append(s)
            continue
        pl, ph, pc, pd = res[-1]
        cl, ch, cc, cd = s
        if float(sp.N(ph)) == float(sp.N(cl)) and (pd or cc):
            res[-1] = [pl, ch, pc, cd]
        else:
            res.append(s)
    return res


def _final_region(coeff_fns, kind, crit):
    segs = _build_segs(coeff_fns, kind, crit)
    out = []
    for lo, hi, clo, chi in segs:
        if lo is not sp.S.NegativeInfinity and _stable_numeric(coeff_fns, float(sp.N(lo, 40)), kind):
            clo = True
        if hi is not sp.S.Infinity and _stable_numeric(coeff_fns, float(sp.N(hi, 40)), kind):
            chi = True
        out.append([lo, hi, clo, chi])
    return _merge(out)


def _verify_region(coeff_fns, kind, segs, crit, samples=140):
    for mid in _midpoints(segs):
        pred = _stable_numeric(coeff_fns, mid, kind)
        if not pred:
            return False
    for lo, hi, clo, chi in segs:
        for p, target in ((lo, clo), (hi, chi)):
            if p is sp.S.NegativeInfinity or p is sp.S.Infinity:
                continue
            if _stable_numeric(coeff_fns, float(sp.N(p, 40)), kind) != bool(target):
                return False
    for _ in range(samples):
        x = random.uniform(-25, 25)
        inside = any(_in_interval(x, s) for s in segs)
        pred = _stable_numeric(coeff_fns, x, kind)
        if inside != pred:
            return False
    for x in crit:
        inside = any(_in_interval(float(sp.N(x)), s) for s in segs)
        if inside != _stable_numeric(coeff_fns, float(sp.N(x)), kind):
            return False
    return True


def _midpoints(segs):
    mids = []
    for lo, hi, clo, chi in segs:
        if lo is sp.S.NegativeInfinity and hi is sp.S.Infinity:
            mids.append(0.0)
        elif lo is sp.S.NegativeInfinity:
            mids.append(float(sp.N(hi)) - 0.01)
        elif hi is sp.S.Infinity:
            mids.append(float(sp.N(lo)) + 0.01)
        else:
            mids.append((float(sp.N(lo)) + float(sp.N(hi))) / 2.0)
    return mids


def _in_interval(x, seg):
    lo, hi, clo, chi = seg
    l = float(sp.N(lo)) if not lo.is_infinite else -float("inf")
    h = float(sp.N(hi)) if not hi.is_infinite else float("inf")
    left = x >= l if clo else x > l
    right = x <= h if chi else x < h
    return left and right


def _fmt_end(v):
    if v is sp.S.Infinity:
        return "inf"
    if v is sp.S.NegativeInfinity:
        return "-inf"
    v = sp.sympify(sp.nsimplify(v))
    if v.is_rational:
        r = sp.Rational(v)
        return str(int(r)) if r == sp.Integer(r) else str(r)
    return format(float(sp.N(v, 40)), ".10g")


def _render_region(segs):
    if not segs:
        return "empty"
    if len(segs) == 1 and segs[0][0] is sp.S.NegativeInfinity and segs[0][1] is sp.S.Infinity:
        return "(-inf,inf)"
    parts = []
    for lo, hi, clo, chi in segs:
        parts.append(("[" if clo else "(") + _fmt_end(lo) + "," + _fmt_end(hi) + ("]" if chi else ")"))
    return " U ".join(parts)


def _parse_region(text):
    if not isinstance(text, str):
        return []
    t = text.strip().lower()
    if not t or t.startswith("empty"):
        return []
    num = r"[-\d./]+|[-+]?inf(?:inity)?"
    pat = re.compile(r"([\[(])\s*(" + num + r")\s*[,:]\s*(" + num + r")\s*([\])])")
    iv = []
    for m in pat.finditer(t):
        lo_s, hi_s = m.group(2), m.group(3)
        lo = -float("inf") if lo_s.strip("- ").startswith("inf") else float(sp.sympify(lo_s))
        hi = float("inf") if hi_s.strip("+ ").startswith("inf") else float(sp.sympify(hi_s))
        iv.append((lo, hi, m.group(1) == "[", m.group(4) == "]"))
    iv.sort(key=lambda q: (q[0], q[1]))
    return iv


def _intervals_equal(a, b, tol=1e-6):
    if len(a) != len(b):
        return False
    for (l1, h1, c1, d1), (l2, h2, c2, d2) in zip(a, b):
        if abs(l1 - l2) > tol or abs(h1 - h2) > tol:
            return False
        if c1 != c2 or d1 != d2:
            return False
    return True


class ParametricRootStabilityV2Config(Config):
    level: int = 0
    degree: int = 2
    slope: int = 1
    const: int = 2
    tdep_frac: float = 0.6

    def apply_difficulty(self, level):
        self.degree = 2 + level // 2
        self.slope = 1 + level
        self.const = 2 + 2 * level
        self.tdep_frac = min(0.85, 0.5 + 0.05 * level)


class ParametricRootStability(Task):
    summary = "Locate every parameter value where a polynomial has all roots in the open left half-plane or unit disk; vary polynomial coefficient dependence, repeated roots, and vanishing leading terms; answer the complete stability region."
    design_choice = "Parameterize coefficients as linear functions of a single scalar t, with stability region found by solving boundary equations."
    config_cls = ParametricRootStabilityV2Config
    task_version = 2

    def render_prompt(self, metadata):
        degree = metadata["degree"]
        cf = metadata["coeff_fns"]
        tex = " + ".join(f"c_{k}(t)*s^{k}" for k in range(degree, -1, -1))
        line = ", ".join(
            f"c_{k}(t) = {a}*t + {b}" if a != 0 else f"c_{k}(t) = {b}"
            for k, (a, b) in enumerate(cf)
        )
        if metadata["kind"] == "hurwitz":
            algo = "Routh-Hurwitz criterion"
            obj = "every root of p_t(s) lies in the open left half-plane (strictly negative real part)"
        else:
            algo = "Jury stability criterion"
            obj = "every root of p_t(s) lies inside the open unit disk (modulus strictly less than 1)"
        return (
            "A parametric real polynomial has coefficients that depend linearly on the scalar t:\n"
            f"p_t(s) = {tex}, where the coefficients are:\n{line}.\n"
            f"Using the {algo}, find the set of all real t for which {obj}.\n"
            "Answer the complete region as a sorted union of disjoint real intervals with exact "
            "endpoints, e.g. '(-1/2, 2] U [3, inf)' or '[-2, 1]'; write 'empty' if no such t exists. "
            "Give the smaller endpoint first in each interval and order intervals left to right."
        )

    def generate_entry(self):
        cfg = self.config
        for _ in range(200):
            n = cfg.degree
            coeff_fns = []
            for k in range(n + 1):
                if k == n:
                    if random.random() < 0.55:
                        a = random.randint(1, max(1, cfg.slope)) * random.choice([-1, 1])
                        b = random.randint(max(1, cfg.const // 2), cfg.const or 1) * random.choice([-1, 1])
                    else:
                        a = 0
                        b = 1
                else:
                    a = random.randint(1, max(1, cfg.slope)) * random.choice([-1, 1])
                    if random.random() > cfg.tdep_frac:
                        a = 0
                    b = random.randint(max(1, cfg.const // 2), cfg.const or 1) * random.choice([-1, 1])
                coeff_fns.append((a, b))
            kind = random.choice(["hurwitz", "schur"])
            crit = _critical_points(coeff_fns, kind)
            if not crit:
                continue
            segs = _final_region(coeff_fns, kind, crit)
            gold = _render_region(segs)
            if gold == "empty" or gold == "(-inf,inf)":
                continue
            if not _verify_region(coeff_fns, kind, segs, crit):
                continue
            raw = [
                [_fmt_end(lo), _fmt_end(hi), int(clo), int(chi)]
                for lo, hi, clo, chi in segs
            ]
            metadata = {
                "degree": n,
                "coeff_fns": [[int(a), int(b)] for a, b in coeff_fns],
                "kind": kind,
                "gold": gold,
                "intervals": raw,
            }
            return Entry(metadata=metadata, answer=gold)
        raise RuntimeError("unable to generate stable instance")


def score_answer(answer, entry):
    if not isinstance(answer, str):
        return 0.0
    parsed = _parse_region(answer)
    ref = _parse_region(entry.metadata["gold"])
    return 1.0 if _intervals_equal(parsed, ref) else 0.0
