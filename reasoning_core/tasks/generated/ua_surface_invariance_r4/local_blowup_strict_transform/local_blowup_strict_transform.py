import random
from dataclasses import dataclass
from math import gcd

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'local_blowup_strict_transform (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_surface_invariance_r4/local_blowup_strict_transform',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _multiplicity_sequence(a, b):
    """Multiplicity sequence of the monomial branch x=t^b, y=t^a under iterated
    point blowups. Subtractive-Euclid reduction on the (a, b) exponent pair:
    each step records min(a, b) (the strict-transform multiplicity), subtracts
    the smaller exponent from the larger, and stops once the minimum is 1
    (the strict transform is smooth). Valid only for coprime exponents,
    guaranteed by the caller."""
    seq = []
    x, y = a, b
    while True:
        m = x if x < y else y
        if m < 2:
            break
        seq.append(int(m))
        if x <= y:
            y -= x
        else:
            x -= y
    return seq


@dataclass
class BlowupConfig(Config):
    max_exp: int = 12

    def apply_difficulty(self, level):
        self.max_exp = 12 + level * 8


class LocalBlowupStrictTransform(Task):
    summary = ("Across implicitly given monomial plane curves y^a = x^b and "
               "parametrized branches x=t^b, y=t^a with coprime exponents a,b>=2, "
               "resolve the marked origin singularity by iterated point blowups and "
               "return the multiplicity sequence of the successive strict transforms.")
    config_cls = BlowupConfig

    def generate_entry(self):
        me = self.config.max_exp
        while True:
            a = random.randint(2, me)
            b = random.randint(2, me)
            if a != b and gcd(a, b) == 1:
                break
        seq = _multiplicity_sequence(a, b)
        if not seq:
            raise RuntimeError("empty multiplicity sequence for min>=2 coprime pair")
        presentation = random.choice(["implicit", "parametrized"])
        answer = " ".join(str(x) for x in seq)
        return Entry(
            metadata={
                "a": a,
                "b": b,
                "presentation": presentation,
                "sequence": seq,
                "depth": len(seq),
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        a = metadata["a"]
        b = metadata["b"]
        if metadata["presentation"] == "implicit":
            curve = f"The implicit plane curve C is given by y^{a} = x^{b}, with gcd({a},{b})=1."
        else:
            curve = (f"The parametrized plane branch C is given by x = t^{b}, y = t^{a}, "
                     f"with integer exponents a={a}, b={b} and gcd({a},{b})=1.")
        return (
            f"{curve} It has a marked singularity at the origin.\n"
            "Resolve C by repeated point blowups at the current singularity: at each "
            "blowup, divide the defining equation by the exceptional factor so that the "
            "curve is reduced (this removes the exceptional divisor), and record the "
            "multiplicity of the resulting strict transform at the new blowup center. "
            "Stop once the strict transform is smooth (multiplicity 1).\n"
            "Return the multiplicity sequence: the list of strict-transform "
            "multiplicities, each an integer at least 2, in the order encountered, "
            "ending when the next strict transform is smooth.\n"
            "Answer as space-separated integers (no brackets), e.g. if the "
            "multiplicities were 3 then 2 before becoming smooth, answer exactly "
            "\"3 2\"."
        )

    def distractor_candidates(self, entry):
        seq = entry.metadata["sequence"]
        yield " ".join(str(x) for x in seq) + " 1"
        yield " ".join(str(x) for x in seq) + " 0"
        yield str(sum(seq))
        yield str(len(seq))
        yield " ".join(reversed([str(x) for x in seq]))
