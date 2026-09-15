import random
import re
from fractions import Fraction
from dataclasses import dataclass
from itertools import product

from reasoning_core.template import Config, Entry, Task, edict

TASK_META = {'parent_source_id': None,
 'idea': 'lie_bracket_hall_normal_form (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r1/lie_bracket_hall_normal_form',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

_GENS = (1, 2, 3)
_CACHE = {}


def _is_lyndon(w):
    for k in range(1, len(w)):
        if not (tuple(w) < tuple(w[k:])):
            return False
    return True


def _lyndon_words(n, length):
    out = []
    for tup in product(range(1, n + 1), repeat=length):
        if _is_lyndon(tup):
            out.append(tup)
    return out


def _std_split(w):
    best = None
    for k in range(1, len(w)):
        if _is_lyndon(w[k:]):
            if best is None or len(w[k:]) > len(w[best:]):
                best = k
    return w[:best], w[best:]


def _brace(w, gens):
    if len(w) == 1:
        return "X%d" % (gens.index(w[0]) + 1)
    u, v = _std_split(w)
    return "[" + _brace(u, gens) + "," + _brace(v, gens) + "]"


def _mul(a, b, c):
    r = {}
    for m1, c1 in a.items():
        for m2, c2 in b.items():
            m = m1 + m2
            if len(m) <= c:
                r[m] = r.get(m, 0) + c1 * c2
    return {m: co for m, co in r.items() if co}


def _comm(a, b, c):
    ab = _mul(a, b, c)
    ba = _mul(b, a, c)
    r = dict(ab)
    for m, co in ba.items():
        r[m] = r.get(m, 0) - co
        if r[m] == 0:
            del r[m]
    return r


def _basis_poly(w, n, c, cache):
    if len(w) == 1:
        res = {w: 1}
        cache[w] = res
        return res
    if w in cache:
        return cache[w]
    u, v = _std_split(w)
    pu = _basis_poly(u, n, c, cache)
    pv = _basis_poly(v, n, c, cache)
    res = _comm(pu, pv, c)
    cache[w] = res
    return res


def _basis(n, c):
    key = (n, c)
    if key in _CACHE:
        return _CACHE[key]
    cache = {}
    words = []
    for d in range(1, c + 1):
        for w in _lyndon_words(n, d):
            words.append(w)
            _basis_poly(w, n, c, cache)
    words.sort(key=lambda w: (len(w), w))
    basis = []
    for w in words:
        basis.append((w, dict(cache[w])))
    _CACHE[key] = basis
    return basis


def _solve_coords(basis_polys, target):
    nv = len(basis_polys)
    monos = set(target)
    for p in basis_polys:
        monos.update(p)
    monos = sorted(monos)
    rows = []
    for mono in monos:
        row = [Fraction(p.get(mono, 0), 1) for p in basis_polys]
        if all(x == 0 for x in row):
            continue
        rows.append([x for x in row] + [Fraction(target.get(mono, 0), 1)])
    num_r = len(rows)
    if num_r == 0:
        return [0] * nv
    A = rows
    row = 0
    for col in range(nv):
        pivot = None
        for i in range(row, num_r):
            if A[i][col] != 0:
                pivot = i
                break
        if pivot is None:
            continue
        A[row], A[pivot] = A[pivot], A[row]
        piv = A[row][col]
        A[row] = [x / piv for x in A[row]]
        for i in range(num_r):
            if i != row and A[i][col] != 0:
                f = A[i][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[row])]
        row += 1
        if row == num_r:
            break
    sol = [0] * nv
    for i in range(row):
        jj = None
        for j in range(nv):
            if A[i][j] == 1:
                jj = j
                break
        if jj is not None:
            sol[jj] = int(A[i][-1])
    return sol


def _tree_poly(node, n, c):
    if node[0] == 'leaf':
        g, co = node[1], node[2]
        return {(g,): co}
    lt, rt = node[1], node[2]
    return _comm(_tree_poly(lt, n, c), _tree_poly(rt, n, c), c)


def _gen_tree(gens, budget, coef_lo, coef_hi):
    if budget == 1:
        g = random.choice(gens)
        co = random.randint(coef_lo, coef_hi)
        if co == 0:
            co = 1
        return ('leaf', g, co)
    L = random.randint(1, budget - 1)
    R = budget - L
    return ('br', _gen_tree(gens, L, coef_lo, coef_hi),
            _gen_tree(gens, R, coef_lo, coef_hi))


def _render_tree(node):
    if node[0] == 'leaf':
        g, co = node[1], node[2]
        nm = "X%d" % g
        if co == 1:
            return nm
        if co == -1:
            return "-" + nm
        return "%d*%s" % (co, nm)
    return "[" + _render_tree(node[1]) + "," + _render_tree(node[2]) + "]"


def _expand(term_list, n, c):
    basis = _basis(n, c)
    target = {}
    for scalar, tree in term_list:
        tp = _tree_poly(tree, n, c)
        for m, co in tp.items():
            target[m] = target.get(m, 0) + scalar * co
    target = {m: co for m, co in target.items() if co}
    coords = _solve_coords([p for _, p in basis], target)
    result = []
    for (w, p), co in zip(basis, coords):
        if co:
            result.append((w, co))
    return result


def _term_render(scalar, tree):
    rt = _render_tree(tree)
    if scalar == 1:
        return rt
    if scalar == -1:
        return "-" + rt
    return "%d*%s" % (scalar, rt)


def _instance_str(term_list):
    parts = []
    for i, (s, t) in enumerate(term_list):
        tr = _term_render(s, t)
        if i == 0:
            parts.append(tr)
        elif tr.startswith("-"):
            parts.append(" - " + tr[1:])
        else:
            parts.append(" + " + tr)
    return "".join(parts)


def _answer_str(n, basis_result, gens):
    if not basis_result:
        return "0"
    parts = []
    basis_lookup = {}
    for w, _ in basis_result:
        basis_lookup[w] = _brace(w, gens)
    # order by (length, word)
    ordered = sorted(basis_result, key=lambda wc: (len(wc[0]), wc[0]))
    first = True
    out = []
    for w, co in ordered:
        br = basis_lookup[w]
        mag = abs(co)
        if co < 0:
            sign = "-" if first else " - "
        else:
            sign = "" if first else " + "
        first = False
        out.append(sign + "%d*%s" % (mag, br))
    return "".join(out)


def _prompt_blocks(n, c, gens):
    basis = _basis(n, c)
    blocks = []
    for idx, (w, _) in enumerate(basis, start=1):
        blocks.append("%d: %s" % (idx, _brace(w, gens)))
    return "; ".join(blocks)


@dataclass
class LieHallConfig(Config):
    n: int = 3
    c: int = 2
    coef_lo: int = -3
    coef_hi: int = 3
    max_leaves: int = 4
    max_terms: int = 2
    max_answer_len: int = 420

    def apply_difficulty(self, level):
        self.n = 3
        self.c = min(3 + level // 2, 4)
        self.max_leaves = min(3 + (level + 1) // 2, self.c)
        self.max_terms = min(2 + level // 3, 3)
        lo = -3 - level
        hi = 3 + level
        self.coef_lo = lo
        self.coef_hi = hi
        self.max_answer_len = 420


class LieBracketHallNormalForm(Task):
    summary = ("Expand nested Lie-bracket expressions in a free nilpotent Lie algebra of "
               "bounded class using bilinearity, antisymmetry, and the Jacobi identity, "
               "returning the canonical Hall-basis linear combination.")
    design_choice = ("Instance format: nested bracket tree with integer coefficients, answer "
                     "as canonical Hall-basis expansion string with coefficients and basis "
                     "elements, e.g., '3*[X1,[X2,X3]] - 2*[X1,X3]'")
    config_cls = LieHallConfig

    def generate_entry(self):
        cfg = self.config
        n, c = cfg.n, cfg.c
        gens = _GENS
        for _ in range(200):
            nterms = random.randint(1, cfg.max_terms)
            term_list = []
            for _t in range(nterms):
                budget = random.randint(2, max(2, cfg.max_leaves))
                tree = _gen_tree(gens, budget, cfg.coef_lo, cfg.coef_hi)
                scalar = random.randint(cfg.coef_lo, cfg.coef_hi)
                if scalar == 0:
                    scalar = 1
                term_list.append((scalar, tree))
            result = _expand(term_list, n, c)
            ans = _answer_str(n, result, gens)
            if ans == "0":
                continue
            if len(ans) > cfg.max_answer_len:
                continue
            if len(result) > 12:
                continue
            if any(abs(co) > 80 for _, co in result):
                continue
            # self-check: faithful re-evaluation must reproduce the input polynomial
            target = {}
            for scalar, tree in term_list:
                tp = _tree_poly(tree, n, c)
                for m, ko in tp.items():
                    target[m] = target.get(m, 0) + scalar * ko
            basis = _basis(n, c)
            recon = {}
            basis_lookup = {w: p for w, p in basis}
            for w, co in result:
                for m, ko in basis_lookup[w].items():
                    recon[m] = recon.get(m, 0) + co * ko
            recon = {m: ko for m, ko in recon.items() if ko}
            target = {m: ko for m, ko in target.items() if ko}
            if recon != target:
                continue
            expr = _instance_str(term_list)
            if expr == "0":
                continue
            metadata = edict({
                "n": n,
                "c": c,
                "expr": expr,
                "basis_blocks": _prompt_blocks(n, c, gens),
                "answer": ans,
            })
            metadata.payload = {
                "c": c,
                "expr": expr,
                "basis_blocks": _prompt_blocks(n, c, gens),
            }
            return Entry(metadata=metadata, answer=ans)
        raise RuntimeError("lie_bracket_hall_normal_form: no admissible instance after resampling")

    def render_prompt(self, metadata):
        return (
            "Work in the free nilpotent Lie algebra of class %d on the generators X1, X2, X3. "
            "The bracket [A,B] is bilinear, antisymmetric ([A,B] = -[B,A], so [A,X] = 0 for any "
            "single generator A), and obeys the Jacobi identity; any bracket whose total depth "
            "exceeds %d vanishes. The canonical Hall basis, given in canonical order, is: %s. "
            "Fully expand the following bracket expression into this canonical basis: %s. "
            "Answer as a linear combination in the exact form 'k1*B1 + k2*B2 - k3*B3' using the "
            "basis element spellings listed above, combining like terms, putting zero terms out, "
            "and ordering the terms by the listed basis order (each coefficient printed even when "
            "it is 1). If the result is zero, answer exactly '0'."
            % (metadata.c, metadata.c, metadata.basis_blocks, metadata.expr)
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        try:
            got = _parse_linear(answer)
            gold = _parse_linear(entry.answer)
        except Exception:
            return 0.0
        if got is None or gold is None:
            return 0.0
        return 1.0 if got == gold else 0.0


_BRACKET_RE = re.compile(r"^\[.*\]$")
_GEN_RE = re.compile(r"^([-+]?\d*)\*?(X\d+)$")


def _split_terms(s):
    terms = []
    cur = ""
    depth = 0
    for ch in s:
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
        if ch in "+-" and depth == 0 and cur.strip() != "":
            terms.append(cur)
            cur = ch
        else:
            cur += ch
    if cur.strip():
        terms.append(cur)
    return terms


def _parse_term(term):
    term = term.strip().replace(" ", "")
    if not term:
        return None
    if "[" in term:
        bi = term.find("[")
        name = term[bi:]
        if not _BRACKET_RE.match(name):
            return None
        coef_str = term[:bi].rstrip("*")
    else:
        mm = _GEN_RE.fullmatch(term)
        if not mm:
            return None
        coef_str, name = mm.group(1), mm.group(2)
    if coef_str in ("", "+", "-"):
        coef = 1 if coef_str in ("", "+") else -1
    else:
        try:
            coef = int(coef_str)
        except ValueError:
            return None
    return (coef, name)


def _parse_linear(s):
    ns = s.replace(" ", "")
    if ns in ("0", "+0", "-0"):
        return {}
    if not ns:
        return None
    terms = _split_terms(s)
    if not terms:
        return None
    result = {}
    for term in terms:
        parsed = _parse_term(term)
        if parsed is None:
            return None
        coef, name = parsed
        result[name] = result.get(name, 0) + coef
    result = {k: v for k, v in result.items() if v}
    return result
