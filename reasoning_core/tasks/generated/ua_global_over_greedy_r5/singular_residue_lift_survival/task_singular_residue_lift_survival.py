import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _primes_below(n):
    sieve = [True] * max(n, 2)
    sieve[0] = sieve[1] = False
    out = []
    for i in range(2, n):
        if sieve[i]:
            out.append(i)
            for j in range(i * i, n, i):
                sieve[j] = False
    return out


_PRIMES = [p for p in _primes_below(400) if p >= 5]


def _eval_mod(poly, r, prime):
    return sum(c * (r ** i) for i, c in enumerate(poly)) % prime


def _deriv_mod(poly, r, prime):
    return sum(i * c * (r ** (i - 1)) for i, c in enumerate(poly) if i > 0) % prime


def _roots_mod_p(poly, prime):
    return [r for r in range(prime) if _eval_mod(poly, r, prime) == 0]


def _lift_single(poly, r, prime, power):
    deriv = _deriv_mod(poly, r, prime)
    if deriv % prime == 0:
        return None
    cur = r
    mod = prime
    inv = pow(deriv, -1, prime)
    for _ in range(power - 1):
        step = mod
        mod *= prime
        fp = _eval_mod(poly, cur, mod)
        k = (fp // step) % prime
        t = (-k * inv) % prime
        cur = (cur + t * step) % mod
    if _eval_mod(poly, cur, mod) != 0:
        return None
    return cur % (prime ** power)


def _lift_all(poly, roots, prime, power):
    out = []
    for r in roots:
        lifted = _lift_single(poly, r, prime, power)
        if lifted is not None:
            out.append(lifted)
    return sorted(set(out))


@dataclass
class SingularResidueLiftSurvivalConfig(Config):
    min_prime: int = 5
    max_prime: int = 397
    min_degree: int = 2
    max_degree: int = 4
    max_power: int = 5

    def apply_difficulty(self, level):
        self.max_degree = 2 + (level // 2)
        self.max_degree = min(self.max_degree, 6)
        self.max_power = 2 + level
        self.max_power = min(self.max_power, 7)


class SingularResidueLiftSurvival(Task):
    summary = "Determine which polynomial roots modulo a prime survive to a specified prime power; track singular branching, merging descriptions and dead ends, returning surviving residues or descendant counts."
    design_choice = "Return the set of surviving residues as a sorted comma-separated list of integers, with empty set as 'none'."
    config_cls = SingularResidueLiftSurvivalConfig
    task_version = 2

    def generate_entry(self):
        while True:
            degree = random.randint(self.config.min_degree, self.config.max_degree)
            prime = random.choice([p for p in _PRIMES if p <= self.config.max_prime])
            power = random.randint(2, self.config.max_power)
            leading = random.choice([1] + [k for k in range(2, 8) if k % prime != 0])
            poly = [random.randint(0, prime - 1) for _ in range(degree)]
            poly.append(leading)

            roots = _roots_mod_p(poly, prime)
            if len(roots) == 0:
                continue

            if all(_deriv_mod(poly, r, prime) == 0 for r in roots):
                continue

            lifted = []
            for r in roots:
                if _deriv_mod(poly, r, prime) % prime != 0:
                    l = _lift_single(poly, r, prime, power)
                    if l is not None:
                        lifted.append(l)
            lifted = sorted(set(lifted))
            for r in lifted:
                if _eval_mod(poly, r, prime ** power) != 0:
                    raise RuntimeError("lift verification failed")

            answer = ",".join(str(r) for r in lifted) if lifted else "none"
            metadata = {
                "poly": [int(c) for c in poly],
                "prime": int(prime),
                "power": int(power),
                "roots_mod_p": [int(r) for r in roots],
                "lifted": [int(r) for r in lifted],
            }
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        poly = metadata["poly"]
        prime = metadata["prime"]
        power = metadata["power"]
        terms = []
        for i, c in enumerate(poly):
            if i == 0:
                terms.append(str(c))
            elif i == 1:
                terms.append(f"{c}x")
            else:
                terms.append(f"{c}x^{i}")
        poly_str = " + ".join(terms)
        return (
            f"Consider the polynomial f(x) = {poly_str} modulo the prime p = {prime}. "
            f"Determine which roots r of f(x) mod {prime} lift (via Hensel lifting) to a root of "
            f"f(x) modulo {prime}^{power}, keeping only those that survive all the way. "
            f"Return the surviving residues modulo {prime}^{power} as a sorted comma-separated "
            f"list of integers, or 'none' if no root survives."
        )

    def score_answer(self, answer, entry):
        gold = entry.answer
        if gold == "none":
            return 1.0 if answer.strip().lower() == "none" else 0.0
        try:
            got = sorted(int(x.strip()) for x in answer.split(",") if x.strip() != "")
        except Exception:
            return 0.0
        want = sorted(int(x) for x in gold.split(","))
        return 1.0 if got == want else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'singular_residue_lift_survival (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_global_over_greedy_r5/singular_residue_lift_survival',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
