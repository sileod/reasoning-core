"""Translate integers between decimal and redundant positional systems."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


balanced_ternary_digits = "012"


def decimal_to_base_n(value, radix):
    """Least-significant-digit-first list of digits of a signed integer in a
    signed radix. For negative radix, digits are non-negative in [0, |radix|)."""
    if value == 0:
        return [0]
    digits_out = []
    n = value
    while n != 0:
        r = n % radix
        n //= radix
        if r < 0:
            r -= radix
            n += 1
        digits_out.append(r)
    return digits_out


def to_balanced_ternary(value):
    """Represent an integer in balanced ternary using digits {0,1,-1}
    represented internally as {-1,0,1}. Returns LSB-first list."""
    if value == 0:
        return [0]
    digits_out = []
    n = value
    while n != 0:
        r = n % 3
        n //= 3
        if r == 2:
            r = -1
            n += 1
        digits_out.append(r)
    return digits_out


def from_balanced_ternary(digits):
    total = 0
    place = 1
    for d in digits:
        total += d * place
        place *= 3
    return total


def from_digits(digits, radix):
    total = 0
    place = 1
    for d in digits:
        total += d * place
        place *= radix
    return total


def to_naf(value):
    """Non-adjacent form. Digits drawn from {0,1,-1}, no two adjacent non-zero.
    Returns LSB-first list."""
    if value == 0:
        return [0]
    digits_out = []
    n = value
    while n != 0:
        if n & 1:
            r = 2 - (n & 3)  # gives -1 or 1 depending on low bits
            n -= r
        else:
            r = 0
        digits_out.append(r)
        n >>= 1
    return digits_out


def from_naf(digits):
    total = 0
    place = 1
    for d in digits:
        total += d * place
        place <<= 1
    return total


def render_signed_digits(digits):
    """Render a list of signed digits as a compact canonical string."""
    return "".join("-1" if d == -1 else str(d) for d in reversed(digits))


def encode_answer(value_str, base_name):
    """value_str is a decimal string; returns canonical answer string in the
    requested system. Digits separated for clarity."""
    return _encode_answer(int(value_str), base_name)


def _encode_answer(value, base_name):
    if base_name == "balanced ternary":
        digits = to_balanced_ternary(value)
        return " ".join("-1" if d == -1 else str(d) for d in reversed(digits))
    if base_name == "base -10":
        digits = decimal_to_base_n(value, -10)
        return " ".join(str(d) for d in reversed(digits))
    if base_name == "base -2":
        digits = decimal_to_base_n(value, -2)
        return " ".join(str(d) for d in reversed(digits))
    if base_name == "NAF":
        digits = to_naf(value)
        return " ".join("-1" if d == -1 else str(d) for d in reversed(digits))
    raise ValueError(base_name)


_BASES = ("balanced ternary", "base -10", "base -2", "NAF")


@dataclass
class TranslationConfig(Config):
    max_abs_value: int = 40

    def apply_difficulty(self, level):
        self.max_abs_value = 40 + level * 300


class NonstandardBaseTranslation(Task):
    summary = ("Translate integers between decimal and redundant positional systems - "
               "balanced ternary, bases -2 and -10, and binary non-adjacent form - in both "
               "directions with growing magnitudes; answer is the exact digit string in the "
               "requested system.")
    design_choice = ("Instances present a decimal integer and request conversion to a "
                     "specified nonstandard base, with the target base chosen randomly per "
                     "instance from the four systems.")
    config_cls = TranslationConfig

    def generate_entry(self):
        base_name = random.choice(_BASES)
        max_abs = self.config.max_abs_value
        value = random.choice(
            [random.randint(-max_abs, max_abs),
             random.choice([random.randint(-max_abs, max_abs),
                            random.randint(-max_abs, max_abs)])]
        )
        if random.random() < 0.15:
            value = 0
        answer = _encode_answer(value, base_name)
        if base_name == "balanced ternary":
            digits = to_balanced_ternary(value)
            assert from_balanced_ternary(digits) == value, (value, digits)
        elif base_name == "base -10":
            digits = decimal_to_base_n(value, -10)
            assert from_digits(digits, -10) == value, (value, digits)
        elif base_name == "base -2":
            digits = decimal_to_base_n(value, -2)
            assert from_digits(digits, -2) == value, (value, digits)
        elif base_name == "NAF":
            digits = to_naf(value)
            assert from_naf(digits) == value, (value, digits)
            for i in range(len(digits) - 1):
                assert not (digits[i] and digits[i + 1]), (value, digits)
        metadata = {
            "value": value,
            "base": base_name,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        base = metadata["base"]
        if base == "NAF":
            base_desc = "binary Non-Adjacent Form (NAF), whose digits are in {-1, 0, 1} and where no two adjacent digits are both non-zero"
        elif base == "balanced ternary":
            base_desc = "balanced ternary, whose digits are in {-1, 0, 1}"
        elif base == "base -2":
            base_desc = "negabinary (base -2), whose digits are in {0, 1}"
        else:
            base_desc = "negadecimal (base -10), whose digits are in {0, 1, 2, 3, 4, 5, 6, 7, 8, 9}"
        return (f"Write the integer {metadata['value']} in {base_desc}. "
                f"Give exactly the digit string in that system, most significant digit "
                f"first, with each digit separated by a space and -1 written as -1. "
                f"For example the integer 5 is written 1 -1 -1 in balanced ternary (5 = 9 - 3 - 1).")

    def score_answer(self, answer, entry):
        gold = entry.answer
        normalized = str(answer).strip()
        if normalized == gold:
            return 1.0
        return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'nonstandard_base_translation (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_semantics_preserving_translation_r1/nonstandard_base_translation',
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
