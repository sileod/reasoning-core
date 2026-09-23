import random
import string
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def manacher_radii(s):
    """Return palindrome radii (full-length, i.e. palindromic radius + 1) around each
    of the 2*n-1 centers (positions and gaps), using mirror reuse against a moving
    right boundary. d2[i] is the odd radius around character i (count of matched
    characters each side, so radius here measured as half-length+... we use the
    classic d1/d2 where the value is the number of characters that extend on each
    side). To keep it length-based and unambiguous we return the full palindrome
    radius as length, not count.
    """
    n = len(s)
    d1 = [0] * n
    l, r = 0, -1
    for i in range(n):
        k = 1 if i > r else min(d1[l + r - i], r - i + 1)
        while i - k >= 0 and i + k < n and s[i - k] == s[i + k]:
            k += 1
        d1[i] = k
        if i + k - 1 > r:
            l, r = i - k + 1, i + k - 1
    d2 = [0] * n
    l, r = 0, -1
    for i in range(n):
        k = 0 if i > r else min(d2[l + r - i + 1], r - i + 1)
        while i - k - 1 >= 0 and i + k < n and s[i - k - 1] == s[i + k]:
            k += 1
        d2[i] = k
        if i + k - 1 > r:
            l, r = i - k, i + k - 1
    return d1, d2


@dataclass
class ManacherConfig(Config):
    length: int = 6
    alphabet: int = 3

    def apply_difficulty(self, level):
        self.length = 7 + level * 2
        self.alphabet = 2 + level


class ManacherPalindromeRadii(Task):
    summary = (
        "Compute palindrome radii around every center of a string using mirror "
        "reuse against a moving right boundary, returning the full radius array, "
        "the radius at a queried center, or the span of the longest palindrome."
    )
    design_choice = (
        "Return the full radius array for all centers of a given string, with "
        "centers indexed by character positions and gaps between them."
    )
    config_cls = ManacherConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.length
        alpha = self.config.alphabet
        pool = string.ascii_lowercase[:alpha]
        while True:
            s = "".join(random.choice(pool) for _ in range(n))
            d1, d2 = manacher_radii(s)
            odd = [2 * v - 1 for v in d1]
            even = [2 * v for v in d2[:-1]]
            ans = odd + even
            if all(a >= 0 for a in ans):
                break
        return Entry(
            metadata={"string": s, "odd": odd, "even": even, "centers": n},
            answer=" ".join(str(x) for x in ans),
        )

    def render_prompt(self, metadata):
        s = metadata["string"]
        n = metadata["centers"]
        return (
            f"Consider the string \"{s}\" of length {n}. Using Manacher's algorithm "
            f"(mirror reuse against a moving right boundary), compute the palindrome "
            f"radius around every center. There are {n} character centers and {n - 1} "
            f"gap centers, for {2 * n - 1} centers total. As the radius around a center "
            f"report the full length of the longest palindrome centered there: for a "
            f"character center this is an odd length, and for a gap center an even "
            f"length. List, in order (character centers 0..{n - 1} first, then gaps), "
            f"all {2 * n - 1} radii separated by single spaces. Example: for the string "
            f"\"aa\" the character radii are 1 1 and the gap radius is 2, so the answer "
            f"is \"1 1 2\". Give only the space-separated list."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        n = entry.metadata["centers"]
        parts = answer.strip().split()
        if len(parts) != 2 * n - 1:
            return 0.0
        try:
            vals = [int(p) for p in parts]
        except ValueError:
            return 0.0
        gold = entry.metadata["odd"] + entry.metadata["even"]
        return 1.0 if vals == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'manacher_palindrome_radii (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_state_tracking_r4/manacher_palindrome_radii',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
