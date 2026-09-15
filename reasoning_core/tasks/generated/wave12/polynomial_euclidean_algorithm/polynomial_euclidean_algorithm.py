"""Polynomial Euclidean algorithm over a fixed small prime field.

Two polynomials over GF(p) are presented as coefficient vectors (highest-degree
first).  The model must run the Euclidean algorithm modulo p, reduce the gcd to
monic form, and report it as a canonical coefficient vector of fixed length
max(deg A, deg B) + 1, highest-degree first, zero-padded to that maximum degree.

Instances are built so their gcd is the constructed monic polynomial g: write
A = g*A1, B = g*B1 with A1, B1 coprime, so gcd(A,B) = g exactly.  The generator
independently recomputes the gcd with modular arithmetic and rejects the draw
unless it equals g (monic) and divides both inputs.
"""

from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict

TASK_META = {'parent_source_id': None,
 'idea': 'polynomial_euclidean_algorithm (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:polynomial_euclidean_algorithm',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/polynomial_euclidean_algorithm',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 924413700,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


P = 7


def _trim(a):
    out = list(a)
    while out and out[-1] % P == 0:
        out.pop()
    return out


def _inv_mod(x):
    x = x % P
    return pow(x, P - 2, P)


def _monic(a):
    a = _trim(a)
    if not a:
        return [0]
    lc = a[-1] % P
    inv = _inv_mod(lc)
    return [(c * inv) % P for c in a]


def _poly_mod(a, b):
    a, b = _trim(a), _trim(b)
    if not a:
        return []
    while len(a) >= len(b):
        k = len(a) - len(b)
        coef = (a[-1] * _inv_mod(b[-1])) % P
        for i in range(len(b)):
            a[i + k] = (a[i + k] - coef * b[i]) % P
        a = _trim(a)
    return a


def _gcd(a, b):
    a, b = _trim(a), _trim(b)
    while b:
        a, b = b, _poly_mod(a, b)
    return _monic(a)


def _poly_mul(a, b):
    a, b = _trim(a), _trim(b)
    res = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            res[i + j] = (res[i + j] + ai * bj) % P
    return res


def _deg(a):
    return len(_trim(a)) - 1


def _random_poly_exact_deg(deg, rng):
    coeffs = [rng.randrange(P) for _ in range(deg)]
    coeffs.append(rng.randrange(1, P))
    return coeffs


def _pad_answer(g_low, max_deg):
    g = _trim(g_low)
    n = max_deg + 1
    padded = (g + [0] * n)[:n]
    while len(padded) < n:
        padded.append(0)
    highest_first = list(reversed(padded))
    return ",".join(str(c) for c in highest_first)


@dataclass
class PolyGcdConfig(Config):
    min_deg: int = 1
    max_deg: int = 2
    min_g_deg: int = 0
    max_g_deg: int = 1

    def apply_difficulty(self, level):
        self.min_deg = 1
        self.max_deg = 2 + level
        self.min_g_deg = 0
        self.max_g_deg = 1 + level // 2


def _parse_answer(answer):
    if answer is None:
        return None
    s = str(answer).strip()
    if not s:
        return None
    s = s.strip("[]")
    parts = [p.strip() for p in s.split(",")]
    if not parts or any(not p.lstrip("+-").isdigit() for p in parts):
        return None
    return [int(p) for p in parts]


def _render_poly(coeffs_high_first):
    return "[" + ", ".join(str(int(c)) for c in coeffs_high_first) + "]"


class PolynomialEuclideanAlgorithm(Task):
    summary = ("Execute exact polynomial division and the Euclidean algorithm over the finite "
               "field GF(7), returning the canonical monic gcd highest-degree-first as an "
               "integer coefficient vector zero-padded to the maximum input degree, across "
               "varied input degrees and gcd degrees from constant to near the smaller input.")
    config_cls = PolyGcdConfig
    task_version = 2
    design_choice = ("Choose coefficients from GF(p) for a fixed small prime p, returning the "
                     "monic gcd in canonical coefficient order with zero-padding to the max degree.")

    def generate_entry(self):
        import random
        cfg = self.config
        min_deg = int(cfg.min_deg)
        max_deg = int(cfg.max_deg)
        min_g = int(cfg.min_g_deg)
        max_g = int(cfg.max_g_deg)

        for _attempt in range(40):
            g_deg = random.randint(min_g, max_g)
            da1 = random.randint(min_deg, max_deg)
            db1 = random.randint(min_deg, max_deg)

            g = _random_poly_exact_deg(g_deg, random) if g_deg >= 0 else [1]
            a1 = _random_poly_exact_deg(da1, random)
            b1 = _random_poly_exact_deg(db1, random)

            A = _poly_mul(g, a1)
            B = _poly_mul(g, b1)

            degA = _deg(A)
            degB = _deg(B)
            max_degree = max(degA, degB)

            gcd_low = _gcd(list(A), list(B))
            want = _monic(list(g))

            ok = (gcd_low == want)
            if ok:
                rA = _poly_mod(list(A), list(want))
                rB = _poly_mod(list(B), list(want))
                if _trim(rA) or _trim(rB):
                    ok = False
            if not ok:
                continue

            ans = _pad_answer(gcd_low, max_degree)
            A_high = list(reversed(_trim(list(A))))
            B_high = list(reversed(_trim(list(B))))
            meta = edict({
                "p": P,
                "a_high": [int(c) % P for c in A_high],
                "b_high": [int(c) % P for c in B_high],
                "gcd_high": [int(c) % P for c in reversed(_trim(list(gcd_low)))],
                "max_degree": int(max_degree),
            })
            meta.payload = {
                "p": P,
                "a": _render_poly([int(c) % P for c in A_high]),
                "b": _render_poly([int(c) % P for c in B_high]),
            }
            return Entry(metadata=meta, answer=ans)

        raise RuntimeError("failed to construct a valid polynomial gcd instance")

    def render_prompt(self, metadata):
        lines = []
        lines.append(f"Work in the finite field GF({metadata.p}) (all arithmetic is modulo "
                     f"{metadata.p}).")
        lines.append("Each polynomial below is written as a coefficient vector listing "
                     "coefficients from the highest-degree term down to the constant term; for "
                     f"example, [3, 0, 2] over GF({metadata.p}) represents 3x^2 + 2.")
        lines.append("")
        lines.append(f"P = {metadata.payload['a']}")
        lines.append(f"Q = {metadata.payload['b']}")
        lines.append("")
        lines.append("Using the Euclidean algorithm, compute the monic greatest common divisor "
                     f"gcd(P, Q) over GF({metadata.p}) and report it as a coefficient vector "
                     "(highest-degree first) of fixed length equal to max(deg P, deg Q) + 1, "
                     "zero-padded to the maximum degree. Give the answer as that integer list, "
                     "e.g. \"0,0,1\".")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = _parse_answer(entry.answer)
        got = _parse_answer(answer)
        if got is None:
            return 0.0
        if len(got) != len(gold):
            return 0.0
        return 1.0 if all(int(g) == int(h) for g, h in zip(got, gold)) else 0.0
