import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'threshold_share_reconstruction (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_uncertainty_r1/threshold_share_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

PRIMES = (7, 11, 13)


@dataclass
class ThresholdShareConfig(Config):
    degree: int = 2
    present: int = 3
    prime: int = 7

    def apply_difficulty(self, level):
        self.degree = stochastic_rounding(self.degree + level)
        self.prime = PRIMES[min(level, len(PRIMES) - 1)]
        self.present = min(self.degree + 1 + level, self.prime)


class ThresholdShareReconstruction(Task):
    summary = ("Recover the constant term of a hidden polynomial mod a small prime "
               "from k of n shares: weight each presented share by its Lagrange "
               "coefficient at zero and sum; share sets meet or exceed the threshold.")
    design_choice = ("Vary the prime among a fixed small set (e.g., 7, 11, 13) and "
                     "present shares as integers in [0,p-1]; answer is the integer constant term.")
    config_cls = ThresholdShareConfig

    def generate_entry(self):
        p = self.config.prime
        degree = self.config.degree
        present = self.config.present
        coeffs = [random.randrange(p) for _ in range(degree + 1)]
        constant = coeffs[0]
        xs = random.sample(range(p), present)
        shares = {}
        for x in xs:
            value = 0
            for i, c in enumerate(coeffs):
                value = (value + c * pow(x, i, p)) % p
            shares[x] = value

        total = 0
        for x, y in shares.items():
            num = 1
            den = 1
            for other in shares:
                if other == x:
                    continue
                num = (num * (0 - other)) % p
                den = (den * (x - other)) % p
            lam = (num * pow(den, p - 2, p)) % p
            total = (total + lam * y) % p
        assert total == constant, (total, constant, p, degree, xs, shares)

        ordering = sorted(shares.keys())
        share_list = [shares[x] for x in ordering]
        xs_list = ordering

        return Entry(
            metadata={
                "prime": p,
                "degree": degree,
                "xs": xs_list,
                "shares": share_list,
                "constant": constant,
                "coeffs": coeffs,
            },
            answer=str(constant),
        )

    def render_prompt(self, metadata):
        pairs = ", ".join(
            f"({x},{y})" for x, y in zip(metadata["xs"], metadata["shares"])
        )
        return (
            f"A secret is shared with Shamir's scheme over the field F_{metadata['prime']}. "
            f"The secret is the constant term of a random polynomial of degree "
            f"{metadata['degree']}. Given the share points {pairs}, compute the secret "
            f"using Lagrange interpolation at x=0. The answer is one integer in [0,"
            f"{metadata['prime'] - 1}]."
        )


def _fixup(entry):
    return entry
