import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _rotations(s):
    n = len(s)
    return [s[i:] + s[:i] for i in range(n)]


def _is_minimal_period(s, per):
    n = len(s)
    if n % per != 0 or s != s[:per] * (n // per):
        return False
    for q in range(1, per):
        if n % q == 0 and s == s[:q] * (n // q):
            return False
    return True


def _canonical(s):
    n = len(s)
    rots = _rotations(s)
    m = min(rots)
    idx = rots.index(m)
    per = 1
    while not _is_minimal_period(s, per):
        per += 1
    order = n // per
    return m, idx, per, order


def _verify(s, canon, idx, per, order):
    n = len(s)
    rots = _rotations(s)
    if canon != min(rots):
        return False
    if rots[idx] != canon:
        return False
    for j in range(idx):
        if rots[j] == canon:
            return False
    if not (1 <= per <= n and 1 <= order <= n):
        return False
    if per * order != n:
        return False
    if not _is_minimal_period(s, per):
        return False
    return True


def _parse_answer(s):
    parts = s.strip().split(",")
    if len(parts) != 4:
        return None
    canon, idx, per, order = parts[0], parts[1], parts[2], parts[3]
    try:
        return canon, int(idx), int(per), int(order)
    except ValueError:
        return None


@dataclass
class NecklaceConfig(Config):
    min_len: int = 4
    max_len: int = 8
    max_alphabet: int = 3
    period_prob: float = 0.5

    def apply_difficulty(self, level):
        self.min_len = 4 + level
        self.max_len = 8 + 2 * level
        self.max_alphabet = 3 + min(level, 3)
        self.period_prob = 0.5


class NecklaceCanonicalRotation(Task):
    summary = ("Canonize cyclic words: for strings with repeated symbols, break the circular "
               "symmetry by reporting the lexicographically least rotation, the earliest index "
               "of it, the primitive period, and the symmetry order, varying alphabet size, "
               "periodicity, and balanced runs.")
    design_choice = ("Report the canonical rotation as the lexicographically smallest rotation, "
                     "breaking ties by the earliest starting index, with the primitive period as "
                     "the minimal period length and symmetry order as length divided by period.")
    config_cls = NecklaceConfig
    task_version = 2
    _alphabet = "abcdefghijklmnopqrstuvwxyz"

    def _build_string(self, n, alphabet):
        a = len(alphabet)
        if random.random() < self.config.period_prob:
            proper = [d for d in range(1, n) if n % d == 0]
            if not proper:
                return "".join(random.choice(alphabet) for _ in range(n))
            p = random.choice(proper)
            block = "".join(random.choice(alphabet) for _ in range(p))
            if not _is_minimal_period(block, p):
                return None
            return block * (n // p)
        else:
            s = "".join(random.choice(alphabet) for _ in range(n))
            if _verify_simple_nonperiodic(s):
                return s
            return None

    def generate_entry(self):
        for _ in range(1000):
            n = random.randint(self.config.min_len, self.config.max_len)
            a = random.randint(2, min(self.config.max_alphabet, n))
            alphabet = self._alphabet[:a]
            s = self._build_string(n, alphabet)
            if s is None:
                continue
            canon, idx, per, order = _canonical(s)
            if not _verify(s, canon, idx, per, order):
                continue
            metadata = {
                "word": s,
                "alphabet_size": a,
                "canonical": canon,
                "index": idx,
                "period": per,
                "order": order,
            }
            answer = ",".join([canon, str(idx), str(per), str(order)])
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("necklace: failed to generate an admissible example")

    def render_prompt(self, metadata):
        word = metadata["word"]
        return (
            f"A string is written around a circle, so its circular rotations are considered the "
            f"same word. Report four values about the word '{word}', separated by commas and in "
            f"exactly this order: (1) the canonical rotation, defined as the lexicographically "
            f"smallest of the word's rotations; (2) the 0-based index in the original string "
            f"'{word}' where that canonical rotation starts, choosing the earliest such index if "
            f"it occurs at more than one place; (3) the primitive period, the length of the "
            f"shortest block that, repeated, generates the whole word; (4) the symmetry order, "
            f"equal to the word length divided by the primitive period. Example: for 'abab' the "
            f"rotations are abab, baba, abab, baba, so the canonical rotation is 'abab' at index "
            f"0, primitive period 2, symmetry order 2, and the answer is abab,0,2,2. The word "
            f"is: {word}"
        )

    def score_answer(self, answer, entry):
        ref = _parse_answer(str(entry.answer))
        got = _parse_answer(str(answer))
        if ref is None or got is None:
            return 0.0
        return 1.0 if got == ref else 0.0

    def distractor_candidates(self, entry):
        s = entry.metadata["word"]
        canon, idx, per, order = entry.metadata["canonical"], entry.metadata["index"], entry.metadata["period"], entry.metadata["order"]
        n = len(s)
        cands = set()
        cands.add(",".join([canon, str(idx), str(order), str(per)]))
        cands.add(",".join([canon, str((idx + per) % n), str(per), str(order)]))
        cands.add(",".join([canon, str(0), str(per), str(order)]))
        return list(cands)


def _verify_simple_nonperiodic(s):
    n = len(s)
    return not _is_minimal_period(s, n)


TASK_META = {'parent_source_id': None,
 'idea': 'necklace_canonical_rotation (draw 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r1/necklace_canonical_rotation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
