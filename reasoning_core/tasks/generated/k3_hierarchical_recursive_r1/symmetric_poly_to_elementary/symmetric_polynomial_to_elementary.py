import itertools
import random
import re

from sympy import Rational

from reasoning_core.template import Config, Entry, Task


TERM_RE = re.compile(r"\(\s*([\d,\s]+)\s*\)\s*:\s*(-?\d+(?:\s*/\s*\d+)?)")


def e_k_poly(k, n):
    result = {}
    for combo in itertools.combinations(range(n), k):
        exp = [0] * n
        for i in combo:
            exp[i] = 1
        result[tuple(exp)] = 1
    return result


def poly_mult(A, B):
    C = {}
    for ea, ca in A.items():
        for eb, cb in B.items():
            ec = tuple(a + b for a, b in zip(ea, eb))
            C[ec] = C.get(ec, 0) + ca * cb
    return {e: c for e, c in C.items() if c}


def e_monomial(mu, n):
    res = {tuple([0] * n): 1}
    for k, p in enumerate(mu, start=1):
        ek = e_k_poly(k, n)
        for _ in range(p):
            res = poly_mult(res, ek)
    return res


def to_elementary(P, n):
    P = {e: Rational(c) for e, c in P.items() if c}
    result = {}
    while P:
        lam, c = max(P.items(), key=lambda kv: kv[0])
        if c == 0:
            del P[lam]
            continue
        mu = tuple(lam[i] - lam[i + 1] for i in range(n - 1)) + (lam[-1],)
        result[mu] = result.get(mu, 0) + c
        emu = e_monomial(mu, n)
        updates = {}
        for e2, c2 in emu.items():
            updates[e2] = P.get(e2, 0) - c * c2
        for e2, val in updates.items():
            if val:
                P[e2] = val
            else:
                P.pop(e2, None)
    return {mu: c for mu, c in result.items() if c}


def reconstruct(result, n):
    P = {}
    for mu, c in result.items():
        emu = e_monomial(tuple(mu), n)
        for e2, c2 in emu.items():
            P[e2] = P.get(e2, 0) + c * c2
    return {e: cc for e, cc in P.items() if cc}


def coeff_str(c):
    c = Rational(c)
    if c.denominator == 1:
        return str(c.numerator)
    return "%s/%s" % (c.numerator, c.denominator)


def parse_answer(s):
    result = {}
    for m in TERM_RE.finditer(s):
        exps = tuple(int(x) for x in re.split(r"[,\s]+", m.group(1).strip()) if x)
        cf = m.group(2)
        if "/" in cf:
            num, den = cf.split("/")
            coeff = Rational(int(num), int(den))
        else:
            coeff = int(cf)
        result[exps] = coeff
    return result


def render_terms(terms):
    out = []
    for mu, c in sorted(terms.items(), key=lambda kv: kv[0], reverse=True):
        out.append("(%s):%s" % (",".join(str(int(v)) for v in mu), coeff_str(c)))
    return "[" + ", ".join(out) + "]"


class SymmetricPolyToElementaryConfig(Config):
    n: int = 2
    max_degree: int = 4
    max_terms: int = 1

    def apply_difficulty(self, level):
        self.n = 2 + level // 3
        self.max_degree = 4 + level
        self.max_terms = 2 + level // 2


class SymmetricPolyToElementary(Task):
    summary = ("Expand symmetric polynomials over Q given as sums of monomial "
               "symmetric functions into the canonical elementary-symmetric-"
               "polynomial expansion by repeated leading-term elimination.")
    design_choice = ("Input representation: give the polynomial as a list of "
                     "(monomial, coefficient) pairs with variables x1..xn, where "
                     "monomials are exponent tuples; output as a list of "
                     "(elementary-basis monomial, coefficient) pairs.")
    config_cls = SymmetricPolyToElementaryConfig

    def _random_partition(self):
        n = self.config.n
        t = random.randint(2, self.config.max_degree)
        cuts = sorted(random.sample(range(1, t + n), n - 1)) if n > 1 else []
        idx = [-1] + cuts + [t + n]
        parts = [idx[i + 1] - idx[i] - 1 for i in range(n)]
        return tuple(sorted(parts, reverse=True))

    def _monomial_symmetric(self, lam):
        d = {}
        for perm in set(itertools.permutations(lam)):
            d[perm] = 1
        return {e: 1 for e in d}

    def generate_entry(self):
        n = self.config.n
        num_terms = random.randint(1, self.config.max_terms)
        P = {}
        for _ in range(num_terms):
            lam = self._random_partition()
            ms = self._monomial_symmetric(lam)
            c = random.choice([1, -1, 1, -1, 2, -2, 1, 3])
            for e, v in ms.items():
                P[e] = P.get(e, 0) + c * v
        P = {e: Rational(v) for e, v in P.items() if v}
        if not P:
            return self.generate_entry()
        expansion = to_elementary(P, n)
        check = reconstruct(expansion, n)
        assert check == P, "answer reconstruction failed"
        degs = sum(lam)  # unused sanity
        meta_terms = sorted(P.items(), key=lambda kv: kv[0], reverse=True)
        metadata = {
            "n": int(n),
            "vars": ["x%d" % (i + 1) for i in range(n)],
            "polynomial": [[list(e), coeff_str(c)] for e, c in meta_terms],
        }
        answer = render_terms(expansion)
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = metadata["n"]
        var_names = metadata["vars"]
        monomials = []
        for exp, c in metadata["polynomial"]:
            factors = []
            for i, v in enumerate(exp):
                if v == 1:
                    factors.append(var_names[i])
                elif v > 1:
                    factors.append("%s^%d" % (var_names[i], v))
            term = "*".join(factors) if factors else "1"
            s = c if c not in ("1", "-1") else ("" if c == "1" else "-")
            monomials.append("%s%s" % (s, term))
        poly_str = " + ".join(monomials).replace("+ -", "- ")
        intro = ("The polynomial P in the variables %s is symmetric, where "
                 "P = %s." % (", ".join(var_names), poly_str))
        prompt = (
            intro +
            " Express P uniquely in the basis of elementary symmetric "
            "polynomials e1, ..., e%d (en is the product of all %d variables). "
            "Output the expansion as a list of terms `(a1,...,an):coeff` meaning "
            "the monomial e1^a1*e2^a2*...*en^an with coefficient coeff, separated "
            "by commas inside square brackets. Coefficients are integers or "
            "fractions like 3/4. Omit zero terms. For example, "
            "[ (1,0,...,0):5 ] means the polynomial equals 5*e1." % (n, n)
        )
        return prompt

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        n = entry.metadata["n"]
        parsed = parse_answer(answer)
        if not parsed:
            return 0.0
        for mu in parsed:
            if not isinstance(mu, tuple) or len(mu) != n:
                return 0.0
        target = {}
        for exp, c in entry.metadata["polynomial"]:
            target[tuple(exp)] = Rational(c)
        try:
            rebuilt = reconstruct(parsed, n)
        except Exception:
            return 0.0
        rebuilt = {e: Rational(v) for e, v in rebuilt.items() if v}
        return 1.0 if rebuilt == target else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'symmetric_polynomial_to_elementary (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/symmetric_polynomial_to_elementary',
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
