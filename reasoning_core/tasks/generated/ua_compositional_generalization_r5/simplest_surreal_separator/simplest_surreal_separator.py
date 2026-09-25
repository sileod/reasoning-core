"""Evaluate finite surreal cuts by finding the earliest-born number strictly between left and right options."""
import random

from reasoning_core.template import Config, Entry, Task


class SimplestSurrealSeparatorV1Config(Config):
    max_magnitude: int = 8
    max_depth: int = 2
    depth: int = 0

    def apply_difficulty(self, level):
        self.max_magnitude = 4 + level * 3
        self.depth = min(level // 2, 2)


def _dyadic_fraction(denom_power):
    num = random.randint(-(1 << denom_power), (1 << denom_power))
    return num / (1.0 * (1 << denom_power))


def _num_to_surreal(value):
    if value == int(value):
        return str(int(value))
    num = round(value * 4)
    if num % 4 == 2:
        return f"{num // 2}/2"
    return f"{num}/4"


def _earliest_between(lo, hi):
    if lo >= hi:
        return None
    k = 1.0
    while k <= 64:
        step = 1.0 / k
        for n in range(int(lo * k) + 1, int(hi * k) + 1):
            cand = n / k
            if lo < cand < hi:
                return cand
        k *= 2
    return None


def _render_surreal(value):
    if value == int(value):
        return str(int(value))
    num = value
    denom = 1.0
    while num != int(num):
        num *= 2
        denom *= 2
    return f"{int(num)}/{int(denom)}"


class SimplestSurrealSeparator(Task):
    summary = ("Evaluate finite surreal cuts by finding the earliest-born number strictly between "
               "their left and right options; vary negative values, dyadic gaps, and nested cuts, "
               "returning the value or an invalid-cut finding.")
    design_choice = ("Answer as a canonical surreal number string (e.g., '3/4', '-1/2') or 'invalid' "
                     "when no such number exists.")
    config_cls = SimplestSurrealSeparatorV1Config
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        while True:
            if cfg.depth <= 0:
                lo = _dyadic_fraction(random.randint(0, 4)) - random.randint(0, cfg.max_magnitude)
            else:
                lo = random.randint(-cfg.max_magnitude - 1, cfg.max_magnitude + 1)
            if random.random() < 0.08:
                hi = lo - _dyadic_fraction(random.randint(1, 4)) - 1
            elif cfg.depth <= 0:
                gap = random.choice([0, 1, 2, 3, 4])
                if gap == 0:
                    hi = random.randint(int(lo) + 1, int(lo) + 2 + random.randint(0, 2))
                else:
                    hi = lo + _dyadic_fraction(gap)
                    if hi <= lo:
                        hi = lo + _dyadic_fraction(gap) + 1
            else:
                delta = random.randint(1, 4)
                hi = lo + delta
                if random.random() < 0.5:
                    hi = lo + delta - _dyadic_fraction(random.randint(1, 4))
                    if hi <= lo:
                        hi = lo + delta

            sep = _earliest_between(lo, hi)
            if sep is None:
                break
            if random.random() < 0.7:
                break
            if random.random() < 0.5:
                lo2 = _earliest_between(lo, sep)
                if lo2 is not None:
                    lo = lo2
        if sep is None:
            answer = "invalid"
        else:
            answer = _render_surreal(sep)
        return Entry(metadata={"left": _render_surreal(lo), "right": _render_surreal(hi)}, answer=answer)

    def render_prompt(self, metadata):
        left = metadata["left"]
        right = metadata["right"]
        return (f"A surreal number is a cut {{ L | R }} with every number in L less than every "
                f"number in R. It is born on the day equal to the smallest nonnegative integer n "
                f"for which its value exists among numbers born on day n; every finite dyadic "
                f"rational is born on a finite day. Consider the cut with left option {left} and "
                f"right option {right}. Find the earliest-born number strictly greater than every "
                f"left option and strictly less than every right option. If no number lies "
                f"strictly between them, making the cut not a proper cut, answer 'invalid'. "
                f"Answer as a canonical surreal value like '3/4' or '-1/2', or the exact string "
                f"'invalid' when no such number exists.")

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'simplest_surreal_separator (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_compositional_generalization_r5/simplest_surreal_separator',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
