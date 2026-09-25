"""Periodic weave reconstruction: recover directional period-and-shift triples."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

LETTERS = "ABCDEFGH"


def necklace_period(s):
    """Smallest cyclic (necklace) period dividing len(s) such that s is periodic."""
    L = len(s)
    for p in range(1, L + 1):
        if L % p:
            continue
        ok = True
        for i in range(L):
            if s[i] != s[(i + p) % L]:
                ok = False
                break
        if ok:
            return p
    return L


def min_rotation_index(c):
    """0-based index of the lexicographically smallest rotation of block c (ties -> first)."""
    n = len(c)
    if n <= 1:
        return 0
    best = 0
    for t in range(1, n):
        for i in range(n):
            a = c[(best + i) % n]
            b = c[(t + i) % n]
            if a < b:
                break
            if a > b:
                best = t
                break
    return best


def periodic_shift(s):
    """Minimal necklace period of s and the seam shift aligning its block to its
    lexicographically smallest rotation."""
    L = len(s)
    for p in range(1, L + 1):
        if L % p:
            continue
        ok = True
        for i in range(L):
            if s[i] != s[(i + p) % L]:
                ok = False
                break
        if ok:
            block = s[:p]
            return p, min_rotation_index(block)
    return L, 0


@dataclass
class WeaveConfig(Config):
    level: int = 0
    max_period: int = 2
    alphabet: int = 2
    length: int = 5

    def apply_difficulty(self, level):
        self.level = level
        self.max_period = 3 + level
        self.alphabet = min(2 + level, 4)
        self.length = 2 * self.max_period + 2 + (level + 1) // 2


class PeriodicWeaveReconstruction(Task):
    summary = ("Unregistered row, column, and diagonal snippets sample a symbol weave "
               "with unknown bounded periods and shifted seams; recover all "
               "period-and-shift triples consistent with one shared pattern.")
    config_cls = WeaveConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        pr = random.randint(2, cfg.max_period)
        pc = random.randint(2, cfg.max_period)
        alpha = cfg.alphabet

        core = [[random.randrange(alpha) for _ in range(pc)] for _ in range(pr)]
        L = cfg.length

        y = random.randrange(pc)
        x0 = random.randrange(pr)
        s_row = [core[(x0 + i) % pr][y] for i in range(L)]

        x = random.randrange(pr)
        y0 = random.randrange(pc)
        s_col = [core[x][(y0 + i) % pc] for i in range(L)]

        d = random.randrange(min(pr, pc))
        s_diag = [core[(d + i) % pr][(d + i) % pc] for i in range(L)]

        p_row, sh_row = periodic_shift(s_row)
        p_col, sh_col = periodic_shift(s_col)
        p_diag, sh_diag = periodic_shift(s_diag)

        answer = f"R:{p_row},{sh_row} C:{p_col},{sh_col} D:{p_diag},{sh_diag}"

        metadata = {
            "row_snippet": "".join(LETTERS[v] for v in s_row),
            "col_snippet": "".join(LETTERS[v] for v in s_col),
            "diag_snippet": "".join(LETTERS[v] for v in s_diag),
            "alphabet": alpha,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            "A periodic symbol weave is built from one shared core pattern. Three "
            "unregistered snippets were sampled from it: a horizontal row snippet, a "
            "vertical column snippet, and a down-right diagonal snippet. Each snippet is "
            "a contiguous run of an infinite periodic string whose symbols repeat and whose "
            "seam is shifted. For each direction, recover the period P and the seam shift S "
            "-- the shift that aligns the snippet's period block to its lexicographically "
            "smallest rotation (rotations counted 0-based, ties by first occurrence). "
            f"Symbols use the alphabet {metadata['alphabet']} letters (A=0, B=1, ...).\n\n"
            f"Row snippet: {metadata['row_snippet']}\n"
            f"Column snippet: {metadata['col_snippet']}\n"
            f"Diagonal snippet: {metadata['diag_snippet']}\n\n"
            "Report the three (period, shift) pairs in the order row, column, diagonal, "
            "as: R:p,s C:p,s D:p,s"
        )

    def score_answer(self, answer, entry):
        reference = entry["answer"]
        return 1.0 if str(answer).strip() == str(reference).strip() else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'periodic_weave_reconstruction (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_interacting_updates_r4/periodic_weave_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4238614268,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
