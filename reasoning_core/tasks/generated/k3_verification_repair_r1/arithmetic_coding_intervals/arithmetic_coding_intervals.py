import random
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'arithmetic_coding_intervals (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/arithmetic_coding_intervals',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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

SYMBOLS = ['a', 'b', 'c']
LOW6 = {'a': 0, 'b': 3, 'c': 5}    # cumulative low bound, numerator over 6
HIGH6 = {'a': 3, 'b': 5, 'c': 6}   # cumulative high bound, numerator over 6


def _encode_intervals(word):
    """Return (lo, hi) as exact Fractions over [0,1) after coding word."""
    lo = Fraction(0)
    hi = Fraction(1)
    for ch in word:
        width = hi - lo
        lo = lo + width * Fraction(LOW6[ch], 6)
        hi = lo + width * Fraction(HIGH6[ch] - LOW6[ch], 6)
    return lo, hi


def _to_common(word, lo, hi):
    """Endpoints as numerators over the common denominator 6^len(word)."""
    den = 6 ** len(word)
    lo_num = int(lo * den)
    hi_num = int(hi * den)
    if hi_num <= lo_num:
        raise RuntimeError('degenerate interval')
    return lo_num, hi_num, den


class ArithmeticCodingConfig(Config):
    word_len_min: int = 3
    word_len_max: int = 3
    mode: str = 'endpoints'

    def apply_difficulty(self, level):
        self.word_len_min = 3
        self.word_len_max = max(min(3 + level, 5), 4)
        self.mode = 'endpoints' if level < 3 else 'inverse'


class ArithmeticCodingIntervals(Task):
    summary = ("Narrow and invert exact rational coding intervals against a cumulative "
               "symbol distribution: encode a short word to its final [lo,hi) endpoints "
               "as fractions, or invert a target rational back into its symbol sequence.")
    design_choice = ("Use a fixed alphabet of 3 symbols with probabilities 1/2,1/3,1/6; "
                     "encode words of length 3-5, ask for endpoints as reduced fractions.")
    config_cls = ArithmeticCodingConfig

    def generate_entry(self):
        while True:
            n = random.randint(self.config.word_len_min, self.config.word_len_max)
            word = ''.join(random.choice(SYMBOLS) for _ in range(n))
            lo, hi = _encode_intervals(word)
            lo_num, hi_num, den = _to_common(word, lo, hi)
            if self.config.mode == 'endpoints':
                metadata = {'mode': 'endpoints', 'word': word, 'lo': lo_num,
                            'hi': hi_num, 'den': den}
                answer = f"{lo_num}/{den} {hi_num}/{den}"
                return Entry(metadata=metadata, answer=answer)
            if random.random() < 0.5:
                metadata = {'mode': 'lo', 'word': word, 'lo': lo_num,
                            'hi': hi_num, 'den': den}
                answer = str(lo_num)
                return Entry(metadata=metadata, answer=answer)
            if hi_num - lo_num >= 2:
                break
        num = random.randrange(lo_num + 1, hi_num)
        if not (lo_num < num < hi_num):
            raise RuntimeError('target not inside interval')
        metadata = {'mode': 'decode', 'word': word, 'target_num': num,
                    'target_den': den}
        answer = word
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        header = ("Arithmetic coding uses the fixed symbol order a, b, c with cumulative "
                  "probabilities a=1/2, b=1/3, c=1/6 over the interval [0,1). Each symbol "
                  "narrows the current interval to its own share.")
        if metadata['mode'] == 'endpoints':
            return (header +
                    f" Code the word \"{metadata['word']}\" by applying each symbol in turn. "
                    f"Report the final interval as the low and high numerators over the "
                    f"common denominator {metadata['den']}, two fractions separated by a "
                    f"space, as in \"3/36 9/36\".")
        if metadata['mode'] == 'lo':
            return (header +
                    f" Code the word \"{metadata['word']}\". After the last symbol, report "
                    f"only the low endpoint's numerator over the denominator "
                    f"{metadata['den']} (an integer).")
        return (header +
                f" The value {metadata['target_num']}/{metadata['target_den']} lies inside "
                f"the final interval of some {len(metadata['word'])}-symbol word. Decode it "
                f"back into its symbol sequence. Answer with the symbols only, no spaces.")

    def score_answer(self, answer, entry):
        mode = entry.metadata['mode']
        if mode == 'decode':
            return 1.0 if str(answer).strip() == entry.metadata['word'] else 0.0
        if mode == 'lo':
            try:
                return 1.0 if int(str(answer).strip()) == entry.metadata['lo'] else 0.0
            except Exception:
                return 0.0
        parts = str(answer).strip().split()
        if len(parts) != 2:
            return 0.0
        try:
            lo_a, hi_a = parts[0], parts[1]
            lo_num_u = int(lo_a.split('/')[0]) / int(lo_a.split('/')[1])
            hi_num_u = int(hi_a.split('/')[0]) / int(hi_a.split('/')[1])
        except Exception:
            return 0.0
        lo_gold = entry.metadata['lo'] / entry.metadata['den']
        hi_gold = entry.metadata['hi'] / entry.metadata['den']
        if abs(lo_num_u - lo_gold) < 1e-12 and abs(hi_num_u - hi_gold) < 1e-12:
            return 1.0
        return 0.0
