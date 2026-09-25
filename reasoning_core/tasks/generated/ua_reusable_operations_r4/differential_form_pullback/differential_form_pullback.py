import itertools
import random
import re
from dataclasses import dataclass

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'differential_form_pullback (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_reusable_operations_r4/differential_form_pullback',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

TARGET_NAMES = ("u", "v", "w")
SOURCE_NAMES = ("x", "y", "z")
INTER_NAMES = ("a", "b", "c")

_TRANSFORMS = standard_transformations

_PLACEHOLDER_LETTERS = [chr(0x41 + i) for i in range(26)]


def _wedge_str(idx, names):
    if not idx:
        return ""
    return "^".join("d" + names[i] for i in idx)


def _sympy_str(expr):
    return sp.sstr(sp.expand(expr))


def _fmt_rational(r):
    r = sp.Rational(r)
    n, d = int(r.p), int(r.q)
    return str(n) if d == 1 else f"{n}/{d}"


def _join_terms(sign_bodies):
    if not sign_bodies:
        return "0"
    s = sign_bodies[0]
    return s


def _format_combine(terms):
    if not terms:
        return "0"
    out = terms[0][0] + terms[0][1] if terms[0][0] else terms[0][1]
    for sign, body in terms[1:]:
        out += sign + body
    return out


def _format_form(rep, names):
    terms = []
    for idx in sorted(rep, key=lambda t: tuple(t)):
        c = sp.Rational(rep[idx])
        if c == 0:
            continue
        neg = c < 0
        body = _fmt_rational(abs(c))
        wedge = _wedge_str(idx, names)
        if wedge:
            body = f"{body}*{wedge}"
        if not terms:
            terms.append(("-" + body if neg else body, ""))
        else:
            terms.append((" - " if neg else " + ", body))
    return _format_combine(terms)


def _format_src_form(src_form, names):
    terms = []
    for c, tup in src_form:
        neg = c < 0
        body = str(abs(int(c)))
        wedge = _wedge_str(tup, names)
        if wedge:
            body = f"{body}*{wedge}"
        if not terms:
            terms.append(("-" + body if neg else body, ""))
        else:
            terms.append((" - " if neg else " + ", body))
    return _format_combine(terms)


def _wedge_expand(oneforms):
    acc = {(): sp.Rational(1)}
    for f in oneforms:
        new = {}
        for coeff, idx in f:
            cv = sp.Rational(coeff)
            if cv == 0:
                continue
            for basis, val in acc.items():
                if idx in basis:
                    continue
                arr = list(basis) + [idx]
                inv = sum(
                    1 for i in range(len(arr))
                    for j in range(i + 1, len(arr)) if arr[i] > arr[j]
                )
                sign = -1 if inv % 2 else 1
                nb = tuple(sorted(arr))
                new[nb] = sp.expand(new.get(nb, sp.Rational(0)) + val * cv * sign)
        acc = new
    return {k: v for k, v in acc.items() if sp.expand(v) != 0}


def _map_coeff(amp):
    r = random.random()
    if r < 0.35:
        v = sp.Rational(random.choice([1, 3, 5]), random.choice([2, 3]))
    else:
        v = sp.Rational(random.randint(1, amp))
    if random.random() < 0.5:
        v = -v
    return v


def _map_expr(target_syms, amp, allow_const=True):
    val = sum(_map_coeff(amp) * t for t in target_syms)
    if allow_const and random.random() < 0.4:
        val += _map_coeff(amp)
    return sp.expand(val)


WEDGE_RE = re.compile(r"d[a-z](?:\^d[a-z])*")


def _wedge_to_idx(wtxt, target_names):
    parts = wtxt.split("^")
    idxs = []
    for p in parts:
        idxs.append(target_names.index(p[1:]))
    return tuple(sorted(idxs))


def _parse_answer(s, target_names):
    if not isinstance(s, str):
        return None
    s = re.sub(r"\s+", "", s.strip())
    if not s:
        return None
    if s == "0":
        return {}
    mapping = {}
    counter = [0]

    def repl(m):
        wedge = m.group(0)
        if wedge not in mapping:
            mapping[wedge] = _PLACEHOLDER_LETTERS[counter[0] % len(_PLACEHOLDER_LETTERS)]
            counter[0] += 1
        return mapping[wedge]

    numeric = WEDGE_RE.sub(repl, s)
    numeric = numeric.replace("+-", "-").replace("-+", "-").replace("++", "+").replace("--", "+")
    try:
        e = parse_expr(numeric, transformations=_TRANSFORMS)
    except Exception:
        return None
    if e == 0:
        return {}
    rep = {}
    try:
        for sym, val in e.as_coefficients_dict().items():
            if not sym.is_Symbol:
                return None
            name = sym.name
            wedge = None
            for w, pn in mapping.items():
                if pn == name:
                    wedge = w
                    break
            if wedge is None:
                return None
            rep[_wedge_to_idx(wedge, target_names)] = sp.Rational(val)
    except Exception:
        return None
    return rep


def _canonical_equal(a, b):
    if a is None or b is None:
        return False
    if set(a) != set(b):
        return False
    for k in a:
        if sp.expand(sp.Rational(a[k]) - sp.Rational(b[k])) != 0:
            return False
    return True


@dataclass
class DifferentialFormPullbackConfig(Config):
    k_max: int = 1
    m_max: int = 2
    n_max: int = 2
    stages: int = 1
    n_terms: int = 1
    amp: int = 3

    def apply_difficulty(self, level):
        self.k_max = 1 + min(1, level // 2)
        self.m_max = 2 + min(1, level // 2)
        self.n_max = 2 + min(1, level // 2)
        self.stages = 1 + min(1, level // 3)
        self.n_terms = 1 + min(2, level // 2)
        self.amp = 3 + min(8, level)


class DifferentialFormPullback(Task):
    summary = ("Transport differential forms through composed coordinate maps using Jacobian "
               "substitution and antisymmetric wedge expansion; vary degrees, dimensions, and "
               "vanishing terms, returning the resulting form.")
    design_choice = ("Answer as a canonical string like '3*x^2*dx^dy + 5*dy^dz' with coefficients "
                     "as fractions and variables ordered lexicographically.")
    config_cls = DifferentialFormPullbackConfig
    task_version = 2

    def generate_entry(self):
        cc = self.config
        for _ in range(300):
            k = random.randint(1, cc.k_max)
            m = random.randint(max(2, k), max(cc.m_max, 2))
            n = random.randint(max(2, k), max(cc.n_max, 2))

            all_sets = list(itertools.combinations(range(m), k))
            if not all_sets:
                continue
            nchoose = min(cc.n_terms, len(all_sets))
            if nchoose < 1:
                continue
            subsets = random.sample(all_sets, nchoose)
            src_form = []
            for st in subsets:
                c = random.choice([-1, 1]) * random.randint(1, cc.amp)
                src_form.append((c, tuple(sorted(st))))

            src_names = SOURCE_NAMES[:m]
            tgt_names = TARGET_NAMES[:n]
            tgt_syms = [sp.Symbol(nm) for nm in tgt_names]
            amp = cc.amp

            inter_names = []
            stage_disp = []
            if cc.stages == 1:
                st_map = {x: _map_expr(tgt_syms, amp) for x in src_names}
                stage_disp.append({x: _sympy_str(st_map[x]) for x in src_names})
                func = [st_map[x] for x in src_names]
            else:
                p = random.randint(1, n)
                inter_names = INTER_NAMES[:p]
                inter_syms = [sp.Symbol(nm) for nm in inter_names]
                map2 = {r: _map_expr(tgt_syms, amp) for r in inter_names}
                map1 = {x: _map_expr(inter_syms, amp) for x in src_names}
                sub = {inter_syms[j]: map2[inter_names[j]] for j in range(p)}
                st_map = {}
                for x in src_names:
                    st_map[x] = sp.expand(map1[x].subs(sub))
                stage_disp.append({x: _sympy_str(map1[x]) for x in src_names})
                stage_disp.append({r: _sympy_str(map2[r]) for r in inter_names})
                func = [st_map[x] for x in src_names]

            J = [[sp.expand(sp.diff(func[i], tgt_syms[j])) for j in range(n)] for i in range(m)]

            final = {}
            for coeff, stuple in src_form:
                oneforms = [[(J[i][j], j) for j in range(n) if J[i][j] != 0] for i in stuple]
                w = _wedge_expand(oneforms)
                for b, val in w.items():
                    final[b] = sp.expand(final.get(b, sp.Rational(0)) + sp.Rational(coeff) * val)
            final = {k: v for k, v in final.items() if sp.expand(v) != 0}
            if not final:
                continue

            gold = _format_form(final, tgt_names)
            goldrep = _parse_answer(gold, tgt_names)
            if not _canonical_equal(goldrep, final):
                raise RuntimeError("gold answer failed to round-trip through parser")

            form_str = _format_src_form(src_form, src_names)
            metadata = {
                "k": k,
                "m": m,
                "n": n,
                "stages": len(stage_disp),
                "form_str": form_str,
                "forms": [[int(c), _wedge_str(t, src_names)] for c, t in src_form],
                "stage_disp": stage_disp,
                "source_names": src_names,
                "target_names": tgt_names,
                "inter_names": inter_names,
                "gold": gold,
            }
            return Entry(metadata=metadata, answer=gold)
        raise RuntimeError("could not build a valid non-vanishing pullback in 300 attempts")


    def render_prompt(self, metadata):
        return _render_prompt(metadata)

    def score_answer(self, answer, entry):
        target_names = entry.metadata.get("target_names")
        if not target_names:
            return 0.0
        gold = _parse_answer(entry.answer, target_names)
        user = _parse_answer(answer, target_names)
        if gold is None or user is None:
            return 0.0
        return 1.0 if _canonical_equal(gold, user) else 0.0


def _render_prompt(metadata):
    form = metadata["form_str"]
    tgt_names = metadata["target_names"]
    src_names = metadata["source_names"]
    n = metadata["n"]
    k = metadata["k"]
    tgt = ", ".join(tgt_names)
    src = ", ".join(src_names)

    stages = metadata["stage_disp"]
    if len(stages) == 1:
        st = stages[0]
        if len(st) == 1:
            lhs, rhs = next(iter(st.items()))
            change = f"{lhs} = {rhs}"
        else:
            change = ", ".join(f"{l} = {r}" for l, r in st.items())
        warps = (
            f"Let the coordinates ({tgt}) and ({src}) be related by the coordinate change "
            f"{change} (each expression is a linear form in the ({tgt}) coordinates)."
        )
    else:
        outer = stages[0]
        inner = stages[1]
        outer_txt = ", ".join(f"{l} = {r}" for l, r in outer.items())
        inner_txt = ", ".join(f"{l} = {r}" for l, r in inner.items())
        inter = metadata["inter_names"]
        intertxt = ", ".join(inter)
        warps = (
            f"Let the coordinates ({src}) be related to auxiliary coordinates ({intertxt}) by "
            f"{outer_txt}, and ({intertxt}) be related to ({tgt}) by {inner_txt} (each expression "
            f"is linear in the coordinates on its right)."
        )

    if k == 1:
        basis = ", ".join(f"{wg}" for wg in (f"d{t}" for t in tgt_names))
    else:
        basis = ", ".join(_wedge_str(c, tgt_names) for c in itertools.combinations(range(n), k))

    return (
        f"{warps}\n\n"
        f"Consider the differential {k}-form on the ({src}) coordinates\n"
        f"ω = {form},\n"
        f"where dx, dy, ... are the coordinate differentials and ^ is the antisymmetric wedge "
        f"product. Compute the pullback of ω through the composition of these coordinate maps "
        f"back to the ({tgt}) coordinates, expanding every differential through the Jacobian "
        f"substitution dx = Σ (∂x/∂t_i) dt_i and antisymmetrically expanding the wedge products "
        f"(du^du = 0, du^dv = -dv^du).\n\n"
        f"Write the answer as a sum of terms `coefficient*basis-wedge` joined by ` + `, where the "
        f"basis wedges are chosen from {basis} with the coordinates in each wedge in ascending "
        f"lexicographic order (e.g. du^dv, not dv^du), coefficients written as exact fractions "
        f"(integers when whole) and negative terms following a ` - ` sign, and every zero term "
        f"omitted. For example a valid answer is `3/2*du^dv - 5*du^dw`.\n\n"
        f"Pullback of ω:"
    )


if __name__ == "__main__":
    pass
