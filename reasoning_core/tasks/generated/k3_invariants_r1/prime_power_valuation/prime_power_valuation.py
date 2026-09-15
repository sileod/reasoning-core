import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'prime_power_valuation (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/prime_power_valuation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _v_p_factorial(n, p):
    s = 0
    while n:
        n //= p
        s += n
    return s


def _v_p_double_factorial(m, p):
    if m <= 0:
        return 0
    m_even = (m % 2 == 0)
    n = m // 2
    if m_even:
        if p == 2:
            return n + _v_p_factorial(n, p)
        return _v_p_factorial(n, p)
    else:
        n = (m + 1) // 2
        two_n = m + 1
        if p == 2:
            return _v_p_factorial(two_n, p) - n - _v_p_factorial(n, p)
        return _v_p_factorial(two_n, p) - _v_p_factorial(n, p)


def _is_prime(p):
    if p < 2:
        return False
    i = 2
    while i * i <= p:
        if p % i == 0:
            return False
        i += 1
    return True


def _careful_div(v, d):
    q, r = divmod(v, d)
    if r != 0:
        raise RuntimeError(f"invalid ratio {v} % {d} != 0")
    return q


@dataclass
class PrimePowerValuationConfig(Config):
    max_n: int = 30

    def apply_difficulty(self, level):
        self.max_n = 16 + 9 * level


class PrimePowerValuation(Task):
    summary = "Compute exact prime-power valuations of factorials, binomials, and double factorials via Legendre floor-sums and base-p carry counts (Kummer), returning the integer exponent."
    design_choice = "Present expressions in symbolic form like n! / (k! (n-k)!) and ask for the p-adic exponent, requiring the solver to identify binomial structure before applying Kummer's theorem."
    config_cls = PrimePowerValuationConfig
    task_version = 2

    def _choose_instance(self):
        max_n = self.config.max_n
        primes = [2, 3, 5, 7, 11, 13]
        for _ in range(400):
            mode = random.choice(["factorial", "binomial", "doublefact"])
            p = random.choice(primes)
            if mode == "factorial":
                n = random.randint(2, max_n)
                num = _v_p_factorial(n, p)
                den = 0
                spec = ("factorial", n, None, p)
            elif mode == "binomial":
                n = random.randint(2, max_n)
                k = random.randint(1, n - 1)
                num = _v_p_factorial(n, p)
                den = _v_p_factorial(k, p) + _v_p_factorial(n - k, p)
                spec = ("binomial", n, k, p)
            else:
                m = random.randint(2, max_n)
                num = _v_p_double_factorial(m, p)
                den = 0
                spec = ("doublefact", m, None, p)
            val = num - den
            if val > 0:
                return spec, val
        raise RuntimeError("could not find nonzero valuation")

    def generate_entry(self):
        (mode, a, b, p), val = self._choose_instance()

        if mode == "factorial":
            expr = f"{a}!"
            check = _v_p_factorial(a, p)
        elif mode == "binomial":
            expr = f"{a}! / ({b}! ({a - b})!)"
            check = _v_p_factorial(a, p) - _v_p_factorial(b, p) - _v_p_factorial(a - b, p)
        else:
            expr = f"{a}!!"
            check = _v_p_double_factorial(a, p)

        if check != val:
            raise RuntimeError("valuation check failed")
        assert isinstance(val, int) and val >= 0

        return Entry(metadata={
            "expr": expr,
            "p": p,
            "value": val,
            "mode": mode,
            "a": a,
            "b": b,
        }, answer=str(val))

    def render_prompt(self, metadata):
        return (
            f"For a positive integer x and prime p, the p-adic valuation v_p(x) is the "
            f"largest integer e such that p^e divides x. Compute v_{metadata['p']} of "
            f"{metadata['expr']}. The answer is one non-negative integer."
        )

    def score_answer(self, answer, entry):
        try:
            v = int(str(answer).strip())
        except (TypeError, ValueError):
            return 0.0
        return 1.0 if v == int(entry["answer"]) else 0.0
