import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'quantizer_preimage_measure (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_novel_composition_r4/quantizer_preimage_measure',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
                                         'version': 'bubblewrap 0.8.0'}}}}

@dataclass
class QuantizerPreimageMeasureConfig(Config):
    level: int = 0
    seed: int = None
    size: int = None
    bins: int = 3
    teeth: int = 1
    base_span: int = 8

    def apply_difficulty(self, level):
        self.bins = 3 + level
        self.teeth = 1 + level
        self.base_span = 8 + 3 * level


def _xs(y, lo, hi, a, b, c_lo, c_hi):
    # smallest x in [lo, hi] with f(x) >= y where f(x) = clip(a*x + b, c_lo, c_hi),
    # represented as a number to clamp against; monotone so preimages are intervals.
    if y <= c_lo:
        return lo
    if y > c_hi:
        return hi
    return (y - b) / a


def _interval_measure(lo, hi, a, b, c_lo, c_hi, t1, t2):
    # measure of {x in [lo, hi] : t1 <= f(x) < t2}
    l = max(lo, _xs(t1, lo, hi, a, b, c_lo, c_hi))
    r = min(hi, _xs(t2, lo, hi, a, b, c_lo, c_hi))
    m = r - l
    return m if m > 0 else Fraction(0)


def _measure_code(lo, hi, a, b, c_lo, c_hi, P, s, j):
    # y = clip(a*x+b, c_lo, c_hi); z = y mod P in [0, P); code = floor(z / s).
    # Measure of inputs whose code equals j (bin width s, bins 0..M-1).
    total = Fraction(0)
    t1j = j * s
    t2j = (j + 1) * s
    k = 0
    while P * k + t1j < c_hi:
        y_lo = P * k + t1j
        y_hi = P * k + t2j
        total += _interval_measure(lo, hi, a, b, c_lo, c_hi, y_lo, y_hi)
        k += 1
        if k > 1_000_000:
            raise RuntimeError("quantizer_preimage_measure: tooth loop did not terminate")
    return total


def _fmt_fraction(fr):
    if fr.denominator == 1:
        return str(fr.numerator)
    return f"{fr.numerator}/{fr.denominator}"


def _parse_fraction(text):
    text = str(text).strip()
    if "/" in text:
        num, den = text.split("/", 1)
        return Fraction(int(num), int(den))
    return Fraction(int(text))


class QuantizerPreimageMeasure(Task):
    summary = ("Invert cascades of affine maps, rounding, clipping, and modular wrapping "
               "over a bounded real interval; return the exact measure of inputs producing "
               "a specified output code.")
    design_choice = ("Answer as a reduced fraction of the interval length, requiring exact "
                     "rational arithmetic for piecewise-constant preimage regions.")
    config_cls = QuantizerPreimageMeasureConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        level = cfg.level
        for _ in range(200):
            hi = random.randint(cfg.base_span, cfg.base_span + 8 + 4 * level)
            lo = 0
            a = Fraction(random.randint(1, 2 + level), random.randint(1, 2 + level))
            b = random.randint(-1 - 3 * level, 1 + 3 * level)
            P = random.randint(2, 4 + level)
            M = cfg.bins
            s = Fraction(P, M)
            c_hi = max(P, cfg.teeth * P)
            c_lo = 0
            j = random.randrange(M)
            measure = _measure_code(lo, hi, a, b, c_lo, c_hi, P, s, j)
            if measure <= 0:
                continue
            total = Fraction(hi - lo)
            answer = measure / total
            if 0 <= answer <= 1:
                break
        else:
            raise RuntimeError("quantizer_preimage_measure: could not produce a positive measure")

        assert 0 <= answer <= 1, answer
        return Entry(
            metadata={
                "lo": lo,
                "hi": hi,
                "a_num": a.numerator,
                "a_den": a.denominator,
                "b": b,
                "c_lo": c_lo,
                "c_hi": c_hi,
                "P": P,
                "M": M,
                "s_num": s.numerator,
                "s_den": s.denominator,
                "code": j,
                "measure_num": measure.numerator,
                "measure_den": measure.denominator,
                "answer_num": answer.numerator,
                "answer_den": answer.denominator,
            },
            answer=_fmt_fraction(answer),
        )

    def render_prompt(self, metadata):
        a = f"{metadata['a_num']}/{metadata['a_den']}"
        s = f"{metadata['s_num']}/{metadata['s_den']}"
        return (
            f"Inputs x are chosen uniformly in the interval [{metadata['lo']}, {metadata['hi']}]. "
            f"A quantizer processes each input as follows: first compute "
            f"f(x) = clip({a}*x + {metadata['b']}, {metadata['c_lo']}, {metadata['c_hi']}) "
            f"(clip below and above), then wrap z = f(x) mod {metadata['P']} into "
            f"[0, {metadata['P']}), then assign code = floor(z / {s}) where the step "
            f"{s} = P / {metadata['M']}, giving codes {metadata['M']} per wrap. "
            f"What fraction of the input interval [{metadata['lo']}, {metadata['hi']}] yields "
            f"output code {metadata['code']}? Give your answer as a reduced fraction of the "
            f"total interval length, e.g. 3/4."
        )

    def score_answer(self, answer, entry):
        try:
            given = _parse_fraction(answer)
            gold = Fraction(str(entry['answer']).strip())
        except Exception:
            return 0.0
        return 1.0 if given == gold else 0.0
