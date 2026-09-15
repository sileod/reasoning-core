import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

PRIMES = (17, 19, 23)


def inv_mod(a, m):
    return pow(a, -1, m)


def point_double(P, a, p):
    if P is None:
        return None
    Px, Py = P
    if Py == 0:
        return None
    lam = (3 * Px * Px + a) * inv_mod(2 * Py, p) % p
    Rx = (lam * lam - 2 * Px) % p
    Ry = (lam * (Px - Rx) - Py) % p
    return (Rx, Ry)


def point_add(P, Q, a, p):
    if P is None:
        return Q
    if Q is None:
        return P
    Px, Py = P
    Qx, Qy = Q
    if Px == Qx and (Py + Qy) % p == 0:
        return None
    lam = (Qy - Py) * inv_mod(Qx - Px, p) % p
    Rx = (lam * lam - Px - Qx) % p
    Ry = (lam * (Px - Rx) - Py) % p
    return (Rx, Ry)


def scalar_mul(k, P, a, p):
    R = None
    for bit in bin(k)[2:]:
        R = point_double(R, a, p)
        if bit == "1":
            R = point_add(R, P, a, p)
    return R


@dataclass
class ScalarMulConfig(Config):
    p_index: int = 0
    scalar_bits: int = 2

    def apply_difficulty(self, level):
        self.p_index = min(level, len(PRIMES) - 1)
        self.scalar_bits = 2 + level


class EllipticCurveScalarMul(Task):
    summary = "Perform scalar multiplication on a Weierstrass elliptic curve over a small prime field via double-and-add; output the resulting point coordinates in affine form."
    design_choice = "Use fixed small prime fields (e.g., p=17, 19) with randomly chosen curve parameters and scalar values, requiring manual modular arithmetic for point doubling and addition."
    config_cls = ScalarMulConfig

    def generate_entry(self):
        p = PRIMES[self.config.p_index]
        while True:
            a = random.randrange(p)
            b = random.randrange(p)
            disc = (4 * a * a * a + 27 * b * b) % p
            if disc != 0:
                break
        while True:
            Gx = random.randrange(p)
            Gy = random.randrange(p)
            if (Gy * Gy - (Gx * Gx * Gx + a * Gx + b)) % p == 0:
                break
        coords = None
        while coords is None:
            k = random.randrange(2, 1 << self.config.scalar_bits)
            try:
                coords = scalar_mul(k, (Gx, Gy), a, p)
            except ValueError:
                coords = None
        Rx, Ry = coords
        return Entry(
            metadata={
                "p": p,
                "a": a,
                "b": b,
                "G": [Gx, Gy],
                "k": k,
            },
            answer=f"{Rx},{Ry}",
        )

    def render_prompt(self, metadata):
        p = metadata["p"]
        a = metadata["a"]
        b = metadata["b"]
        Gx, Gy = metadata["G"]
        k = metadata["k"]
        return (
            f"On the elliptic curve y^2 = x^3 + {a}x + {b} over the field F{p}, "
            f"compute the point k*G = {k}*({Gx},{Gy}) using double-and-add with "
            f"modular arithmetic mod {p}. Give the result as the affine coordinates "
            f"x,y (two integers separated by a comma)."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        s = str(answer).strip()
        return 1.0 if s == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'elliptic_curve_scalar_mul (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r1/elliptic_curve_scalar_mul',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
