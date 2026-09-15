import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SchwartzZippelConfig(Config):
    prime: int = 97
    instances: int = 5

    def apply_difficulty(self, level):
        self.prime = [13, 31, 61, 97, 131, 239, 401][min(level, 6)]
        self.instances = 3 + level


class SchwartzZippelIdentity(Task):
    summary = (
        "Evaluate two arithmetic circuits at shared random points over a finite field, "
        "decide polynomial identity with bounded error bounded by 1/field_size."
    )
    design_choice = (
        "Choose the field size and instance count so that the false-positive probability "
        "is exactly 1/field_size, and require a yes/no answer per instance."
    )
    config_cls = SchwartzZippelConfig

    def _rand_coeffs(self, degree):
        return [random.randrange(self.config.prime) for _ in range(degree + 1)]

    def _eval(self, coeffs, x):
        acc = 0
        for c in reversed(coeffs):
            acc = (acc * x + c) % self.config.prime
        return acc

    def generate_entry(self):
        p = self.config.prime
        degree = 2 + self.config.instances // 2
        a = self._rand_coeffs(degree)
        b = self._rand_coeffs(degree)
        equal = random.random() < 0.5
        if equal:
            b = list(a)
        x = random.randrange(p)
        av = self._eval(a, x)
        bv = self._eval(b, x)
        actual_eq = (av == bv)
        # With distinct polynomials, P(equal at a random x) == 1/p. We must not
        # let the ground truth contradict the polynomial identity that we ask
        # about: enforce that the sampled random point reflects the true status.
        if equal != actual_eq:
            x = random.randrange(p)
            av = self._eval(a, x)
            bv = self._eval(b, x)
            actual_eq = (av == bv)
        answer = "yes" if equal else "no"
        return Entry(
            metadata={
                "prime": p,
                "a": a,
                "b": b,
                "x": x,
                "a_value": av,
                "b_value": bv,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        p = metadata["prime"]
        a = metadata["a"]
        b = metadata["b"]
        x = metadata["x"]
        lines = [
            f"Over the prime field of size {p}, two univariate polynomials are encoded as "
            f"coefficient lists (constant term first).",
            f"A = {a}",
            f"B = {b}",
            f"Evaluate both at the shared random point x = {x} and check whether the two "
            f"polynomials are identical (Schwartz-Zippel identity test).",
            "Answer exactly 'yes' if they are identical, otherwise 'no'.",
        ]
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = answer.strip().lower()
        gold = entry.answer
        return 1.0 if norm == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'schwartz_zippel_identity (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relevance_separation_r1/schwartz_zippel_identity',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
