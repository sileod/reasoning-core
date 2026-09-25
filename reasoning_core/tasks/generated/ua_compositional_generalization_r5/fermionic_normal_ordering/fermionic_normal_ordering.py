import random
import re
from collections import defaultdict
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'fermionic_normal_ordering (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r5/fermionic_normal_ordering',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _normalize_monomial(ops):
    """Return dict {(cs_tuple, a_tuple): coeff} for the normal-ordered form of ops."""
    result = defaultdict(int)
    queue = [(list(ops), 1)]
    while queue:
        mono, coeff = queue.pop()
        n = len(mono)
        fixed = False
        for i in range(n - 1):
            (xk, xm), (yk, ym) = mono[i], mono[i + 1]
            if xk == 'A' and yk == 'C':
                m2 = mono[:i] + [mono[i + 1], mono[i]] + mono[i + 2:]
                queue.append((m2, -coeff))
                if xm == ym:
                    m3 = mono[:i] + mono[i + 2:]
                    queue.append((m3, coeff))
                fixed = True
                break
            if xk == yk and xm > ym:
                if xm == ym:
                    fixed = True
                    break
                m2 = mono[:i] + [mono[i + 1], mono[i]] + mono[i + 2:]
                queue.append((m2, -coeff))
                fixed = True
                break
        if fixed:
            continue
        cs = sorted(xm for xk, xm in mono if xk == 'C')
        a = sorted(xm for xk, xm in mono if xk == 'A')
        if len(set(cs)) != len(cs) or len(set(a)) != len(a):
            continue
        result[(tuple(cs), tuple(a))] += coeff
    return result


def _normalize_expr(monomials):
    out = defaultdict(int)
    for mono in monomials:
        for key, c in _normalize_monomial(mono).items():
            out[key] += c
    return {k: v for k, v in out.items() if v != 0}


def _signed(cs, a, coeff):
    body = "".join("c%d" % i for i in cs) + "".join("a%d" % i for i in a)
    if not body:
        return str(coeff)
    if coeff == 1:
        return body
    if coeff == -1:
        return "-" + body
    return "%d*%s" % (coeff, body)


def _render_result(d):
    keys = sorted(d.keys(), key=lambda k: (len(k[0]), len(k[1]), k[0], k[1]))
    parts = [_signed(k[0], k[1], d[k]) for k in keys]
    if not parts:
        return "0"
    return " + ".join(parts).replace(" + -", " - ").strip()


def _monomial_str(mono):
    return "".join(("c" if k == 'C' else "a") + ("%d" % m) for k, m in mono)


def _render_expr(monomials):
    chunks = []
    for mono in monomials:
        s = _monomial_str(mono)
        if len(mono) >= 4 and random.random() < 0.4:
            s = "(" + s + ")"
        chunks.append(s)
    return " + ".join(chunks)


def _canonical_from_metadata(canonical):
    return {
        (tuple(cs), tuple(a)): coeff
        for coeff, cs, a in canonical
    }


def _parse_answer(s):
    s = re.sub(r"\s+", "", s)
    if not s:
        return None
    terms = []
    cur = ""
    sign = 1
    for ch in s:
        if ch in "+-":
            if terms or cur:
                terms.append((sign, cur))
            sign = 1 if ch == "+" else -1
            cur = ""
        else:
            cur += ch
    if cur or not terms:
        terms.append((sign, cur))
    d = defaultdict(int)
    for sign, term in terms:
        if not term:
            continue
        m = re.match(r"^([0-9]*)", term)
        numstr = m.group(1)
        rest = term[len(numstr):]
        if rest.startswith("*"):
            rest = rest[1:]
        if not rest:
            d[((), ())] += sign * (int(numstr) if numstr else 1)
            continue
        base = int(numstr) if numstr else 1
        cs, a = [], []
        pos = 0
        ok = True
        for m2 in re.finditer(r"c(\d+)|a(\d+)", rest):
            if m2.start() != pos:
                ok = False
                break
            if m2.group(1) is not None:
                cs.append(int(m2.group(1)))
            else:
                a.append(int(m2.group(2)))
            pos = m2.end()
        if not ok or pos != len(rest):
            return None
        d[(tuple(sorted(cs)), tuple(sorted(a)))] += sign * base
    return {k: v for k, v in d.items() if v != 0}


def _phase(bits, mode):
    return 1 if bin(bits & ((1 << mode) - 1)).count("1") % 2 == 0 else -1


def _ann(mode, bits):
    if bits & (1 << mode):
        return _phase(bits, mode), bits & ~(1 << mode)
    return 0, None


def _cre(mode, bits):
    if not (bits & (1 << mode)):
        return _phase(bits, mode), bits | (1 << mode)
    return 0, None


def _apply_seq(seq, state):
    acc = {state: 1}
    for op, mode in reversed(seq):
        new = defaultdict(int)
        for st, c in acc.items():
            w, ns = (_cre(mode, st) if op == 'C' else _ann(mode, st))
            if w and ns is not None:
                new[ns] += c * w
        acc = new
    return acc


def _verified(monomials, canonical):
    for (cs, a), coeff in canonical.items():
        if len(set(cs)) != len(cs) or len(set(a)) != len(a):
            return False
    nmode = 0
    for mono in monomials:
        for _, m in mono:
            nmode = max(nmode, m + 1)
    for state in range(1 << nmode):
        inp = defaultdict(int)
        for mono in monomials:
            for st, c in _apply_seq(mono, state).items():
                inp[st] += c
        cand = defaultdict(int)
        for (cs, a), coeff in canonical.items():
            seq = [('C', m) for m in cs] + [('A', m) for m in a]
            for st, c in _apply_seq(seq, state).items():
                cand[st] += coeff * c
        if dict(inp) != dict(cand):
            return False
    return True


@dataclass
class FermionicConfig(Config):
    min_ops: int = 2
    max_ops: int = 3
    min_monos: int = 1
    max_monos: int = 1
    modes: int = 3

    def apply_difficulty(self, level):
        self.min_ops = 2
        self.max_ops = 3 + level // 2
        self.min_monos = 1
        self.max_monos = 1 + level // 2
        self.modes = 3


class FermionicNormalOrdering(Task):
    summary = ("Normalize products of fermionic creation and annihilation operators to a "
               "canonical sum of uniquely ordered monomials with integer coefficients via "
               "anticommutation, contraction and nilpotency, varying repeated modes, nested "
               "products and sums.")
    config_cls = FermionicConfig
    task_version = 2
    design_choice = ("Answer as a canonical sum of uniquely ordered monomials with integer "
                     "coefficients, where each monomial lists creation operators before "
                     "annihilation operators in fixed mode order, and identical terms are "
                     "combined.")

    def generate_entry(self):
        cfg = self.config
        for _ in range(60):
            n_monos = random.randint(cfg.min_monos, cfg.max_monos)
            monomials = []
            for _m in range(n_monos):
                n_ops = random.randint(cfg.min_ops, cfg.max_ops)
                mono = []
                for _o in range(n_ops):
                    kind = random.choice(('C', 'A'))
                    mode = random.randrange(cfg.modes)
                    mono.append((kind, mode))
                monomials.append(mono)
            canonical = _normalize_expr(monomials)
            if not canonical:
                continue
            if not _verified(monomials, canonical):
                continue
            nmode = 0
            for mono in monomials:
                for _, m in mono:
                    nmode = max(nmode, m + 1)
            answer = _render_result(canonical)
            canonical_sorted = sorted(
                ((coeff, list(cs), list(a))
                 for (cs, a), coeff in canonical.items()),
                key=lambda t: (len(t[1]), len(t[2]), tuple(t[1]), tuple(t[2])),
            )
            metadata = {
                "monomials": [[[k, m] for k, m in mono] for mono in monomials],
                "expression": _render_expr(monomials),
                "modes": nmode,
                "canonical": canonical_sorted,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("failed to generate a valid fermionic normal ordering task")

    def render_prompt(self, metadata):
        return (
            "Fermionic normal ordering rewrites a product of creation operators c_i and "
            "annihilation operators a_i (i a mode index) into an equal operator with every "
            "creation to the left of every annihilation, using the anticommutation move "
            "a_i c_j = delta_{ij} - c_j a_i, the sign rules c_i c_j = -c_j c_i and "
            "a_i a_j = -a_j a_i for i != j, and nilpotency c_i c_i = a_i a_i = 0; contractions "
            "(a paired with c of the same mode) become the vacuum value 1.\n"
            "Write the normal ordering as a sum of monomials with integer coefficients. In each "
            "monomial list the creations (c_i, increasing mode) then the annihilations "
            "(a_i, increasing mode), multiplied by its integer coefficient; a lone integer is the "
            "constant term; drop zero coefficients; combine identical monomials; and order the "
            "monomials by (number of creations, number of annihilations, creation modes, "
            "annihilation modes). Format example: '1 - c0a0' is the normal ordering of a0 c0.\n"
            "Expression: %s\n"
            "What is the normal ordering of %s? "
            "Answer as the canonical sum of uniquely ordered monomials with integer coefficients."
            % (metadata["expression"], metadata["expression"])
        )

    def score_answer(self, answer, entry):
        parsed = _parse_answer(answer)
        if parsed is None:
            return 0.0
        gold = _canonical_from_metadata(entry.metadata.get("canonical"))
        return 1.0 if parsed == gold else 0.0
