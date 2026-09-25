import ast
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _signature(w, i):
    """Bracket-match the i/i+1 subword of the reading word w.

    Letters equal to i are treated as opening brackets, letters equal to i+1
    as closing brackets; each opening is matched with the nearest unmatched
    closing after it in reading order. Returns (matched positions, tuple of
    unmatched-i (opening) positions in reading order, unmatched-(i+1) count).
    """
    stack = []
    matched = set()
    for pos, letter in enumerate(w):
        if letter == i:
            stack.append(pos)
        elif letter == i + 1 and stack:
            matched.add(stack.pop())
            matched.add(pos)
    unmatched_i = tuple(p for p in stack)
    unclosed = sum(1 for pos, letter in enumerate(w)
                   if letter == i + 1 and pos not in matched)
    return matched, unmatched_i, unclosed


def _raise_chain(word, i):
    """Apply e_i repeatedly until it becomes a null move.

    Returns (final word, tuple of reading-word positions that changed, in
    the order they changed).
    """
    wl = list(word)
    changed = []
    while True:
        matched, unmatched_i, _unclosed = _signature(wl, i)
        if not unmatched_i:
            break
        pos = unmatched_i[-1]  # rightmost unmatched i
        if wl[pos] != i:
            raise RuntimeError("signature mismatch")
        wl[pos] = i + 1
        changed.append(pos)
    return wl, tuple(changed)


def _verify(word, i, final_word, positions):
    if not (0 <= len(positions)):
        raise RuntimeError("bad positions")
    wl = list(word)
    for p in positions:
        if not (0 <= p < len(word)):
            raise RuntimeError("position out of range")
        if wl[p] != i:
            raise RuntimeError("changed cell was not an i")
        matched, unmatched_i, _u = _signature(wl, i)
        if not unmatched_i or unmatched_i[-1] != p:
            raise RuntimeError("changed cell was not the rightmost unmatched i")
        wl[p] = i + 1
    if wl != final_word:
        raise RuntimeError("chain simulation diverged")
    matched, unmatched_i, _u = _signature(wl, i)
    if unmatched_i:
        raise RuntimeError("final word still admits e_i")
    if len(set(positions)) != len(positions):
        raise RuntimeError("duplicate positions")


@dataclass
class CrystalSignatureConfig(Config):
    max_n: int = 2
    max_dim: int = 2

    def apply_difficulty(self, level):
        self.max_n = 3 + level
        self.max_dim = 3 + level


class CrystalSignatureTransfer(Task):
    summary = ("Execute crystal raising on bottom-to-top reading words of letter grids via "
               "signature cancellation on i/i+1 subwords (interlacing patterns, matched and "
               "unmatched brackets), chaining rightmost-unmatched-i raises to a null move; "
               "return the changed cell coordinates with null moves omitted.")
    design_choice = ("Return the list of cell coordinates whose entries change after applying "
                     "a raising operator, with null moves omitted.")
    config_cls = CrystalSignatureConfig

    def generate_entry(self):
        n = random.randint(2, self.config.max_n)
        i = random.randint(1, n - 1)
        h = random.randint(2, self.config.max_dim)
        wd = random.randint(2, self.config.max_dim)
        length = h * wd
        word = [random.randint(1, n) for _ in range(length)]
        word[random.randrange(length)] = i
        word[random.randrange(length)] = i + 1
        final_word, positions = _raise_chain(word, i)
        _verify(word, i, final_word, positions)
        coords = [[h - 1 - (p // wd), p % wd] for p in positions]
        grid = [word[r * wd:(r + 1) * wd] for r in range(h)]
        metadata = {
            "n": n,
            "i": i,
            "rows": h,
            "cols": wd,
            "grid": grid,
            "word": word,
            "reading_order": "bottom-to-top",
            "changed_coords": coords,
        }
        return Entry(metadata=metadata, answer=str(coords))

    def render_prompt(self, metadata):
        lines = []
        lines.append("A word is written into a grid of cells; each cell holds a letter from "
                     "the alphabet {1, ..., %d}." % metadata["n"])
        lines.append("The reading word is read BOTTOM row to TOP row, left to right within "
                     "each row (bottom-to-top reading word).")
        lines.append("")
        lines.append("Apply the crystal RAISING operator e_i for i = %d. Its signature rule: "
                     "restrict the reading word to the two letters i and i+1; bracket-match "
                     "each letter i with the nearest unmatched letter i+1 after it (matched "
                     "pairs are removed). Of the letters that remain unmatched, e_i changes "
                     "the RIGHTMOST unmatched i into i+1. If no i is unmatched, e_i is a null "
                     "move and changes nothing." % metadata["i"])
        lines.append("Apply e_i over and over until it becomes a null move.")
        lines.append("")
        lines.append("List the cell coordinates [row, column] of the entries that change, in "
                     "the order they change (0-indexed row counted from the top, column from "
                     "the left). If nothing changes, answer [].")
        lines.append("")
        lines.append("Worked example of the answer FORMAT: for i = 1 in the 2x3 grid below "
                     "(reading word 1 2 1 1 3 1, bottom row first) the entries that change "
                     "are cell [0,2] (the letter 1 in the top row) then cell [1,2] (the "
                     "letter 1 in the bottom row), so the answer is [[0, 2], [1, 2]].")
        lines.append("")
        for r in range(metadata["rows"]):
            lines.append("row %d: %s" % (r, metadata["grid"][r]))
        lines.append("")
        lines.append("i = %d, alphabet size n = %d." % (metadata["i"], metadata["n"]))
        return "\n".join(lines)


def _parse_coords(answer):
    if isinstance(answer, str):
        answer = answer.strip()
    try:
        vals = ast.literal_eval(answer)
    except (ValueError, SyntaxError, TypeError):
        return None
    if not isinstance(vals, list):
        return None
    out = []
    for item in vals:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            return None
        try:
            out.append([int(item[0]), int(item[1])])
        except (TypeError, ValueError):
            return None
    return out


    def score_answer(self, answer, entry):
        gold = entry.metadata["changed_coords"]
        got = _parse_coords(answer)
        if got is None:
            return 0.0
        return 1.0 if got == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'crystal_signature_transfer (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/crystal_signature_transfer',
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
