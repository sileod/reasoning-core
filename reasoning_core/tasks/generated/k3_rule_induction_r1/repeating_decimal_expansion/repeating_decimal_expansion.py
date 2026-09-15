import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'repeating_decimal_expansion (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_rule_induction_r1/repeating_decimal_expansion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def long_division(numerator, denominator):
    """Return (integer_part, preperiod_digits, repetend_digits)."""
    sign = -1 if (numerator < 0) != (denominator < 0) else 1
    n = abs(numerator)
    d = abs(denominator)
    integer_part = n // d
    rem = n % d
    seen = {}
    preperiod = []
    repetend = []
    i = 0
    while rem != 0:
        if rem in seen:
            start = seen[rem]
            repetend = preperiod[start:]
            preperiod = preperiod[:start]
            return sign, integer_part, preperiod, repetend
        seen[rem] = i
        rem *= 10
        preperiod.append(str(rem // d))
        rem = rem % d
        i += 1
    return sign, integer_part, preperiod, repetend


def format_expansion(sign, integer_part, preperiod, repetend):
    digits = "".join(preperiod)
    body = f"{integer_part}.{digits}"
    if repetend:
        body = f"{integer_part}.{digits}({''.join(repetend)})"
    if sign < 0:
        body = "-" + body
    return body


@dataclass
class RepeatingDecimalConfig(Config):
    num_min: int = 11
    num_max: int = 999
    density: float = 0.6

    def apply_difficulty(self, level):
        self.num_min = 11 + 4 * level
        self.num_max = 20 + 140 * level
        self.density = stochastic_rounding(self.density + 0.05 * level)


class RepeatingDecimalExpansion(Task):
    summary = ("Carry out long division of one integer by another, detecting the first repeated "
               "remainder to split the decimal expansion into integer part, preperiod, and minimal "
               "repetend, over terminating, purely recurring, and mixed cases.")
    design_choice = ("Answer as a single canonical string like '12.3(45)' where parentheses enclose "
                     "the minimal repetend, with no decimal point for integer-only results")
    task_version = 2
    config_cls = RepeatingDecimalConfig

    def generate_entry(self):
        c = self.config
        while True:
            den = random.randint(2, c.num_max)
            num = random.randint(c.num_min, c.num_max)

            def _gcd(a, b):
                while b:
                    a, b = b, a % b
                return a

            g = _gcd(num, den)
            reduced = den // g
            t = reduced
            while t % 2 == 0:
                t //= 2
            while t % 5 == 0:
                t //= 5
            if t == 1:
                mode = "terminating"
            else:
                if _gcd(num, den) != 1:
                    continue
                mode = random.choice(["pure", "mixed"])
                if mode == "mixed":
                    while reduced % 2 == 0:
                        reduced //= 2
                    while reduced % 5 == 0:
                        reduced //= 5
                    if reduced == 1:
                        continue
            sign, integer_part, preperiod, repetend = long_division(num, den)
            if mode == "terminating":
                if repetend:
                    continue
            elif mode == "pure":
                if preperiod or not repetend:
                    continue
            else:
                if not preperiod or not repetend:
                    continue
            answer = format_expansion(sign, integer_part, preperiod, repetend)
            metadata = {
                "numerator": num,
                "denominator": den,
                "mode": mode,
                "integer_part": str(integer_part),
                "preperiod": "".join(preperiod),
                "repetend": "".join(repetend),
                "answer": answer,
            }
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (f"Divide {metadata['numerator']} by {metadata['denominator']} using long division "
                f"and write the decimal expansion. Enclose the minimal repeating part (repetend) in "
                f"parentheses, e.g. 1/3=0.(3), 1/6=0.1(6), 1/8=0.125. If the result is an integer, "
                f"write it with no decimal point. Give only the answer.")

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0
