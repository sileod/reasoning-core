"""Tower block removal: static center-of-mass toppling analysis.

A single column of axis-aligned blocks rests on an infinite ground. Each block has a
width, a mass, and a signed horizontal offset of its center relative to the block
directly below it. Removing one block or nudging one block (shifting its center
horizontally) forces a re-check of every support interface above the change; the toppled
set is the maximum suffix that loses center-of-mass support. The answer is the sorted
list of toppled block IDs and the height (number of blocks) of the surviving stack.
"""

import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'tower_block_removal (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_specific_r1/tower_block_removal',
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


def _com(X, masses, ids):
    total = sum(masses[j] for j in ids)
    return Fraction(sum(X[j] * masses[j] for j in ids), total)


def _interface_fail(X, w, masses, above, i):
    com = _com(X, masses, above)
    half = Fraction(w[i], 2)
    return not (Fraction(X[i]) - half < com < Fraction(X[i]) + half)


def _simulate(X0, w, masses, action, n):
    present = list(range(n))
    X = list(X0)
    kind = action[0]
    if kind == 'remove':
        present.remove(action[1])
    else:
        idx, delta = action[1], action[2]
        X[idx] += delta
    present.sort()
    for pos, i in enumerate(present[:-1]):
        above = present[pos + 1:]
        if _interface_fail(X, w, masses, above, i):
            topple = present[pos + 1:]
            survivors = present[:pos + 1]
            return topple, survivors, X
    return [], present, X


def _verify(X, w, masses, present, topple):
    for pos, i in enumerate(present[:-1]):
        above = present[pos + 1:]
        fails = _interface_fail(X, w, masses, above, i)
        if topple:
            boundary = present[(present.index(topple[0]) - 1)]
            if i == boundary:
                if not fails:
                    return False
                continue
        if fails:
            return False
    if not topple:
        return True
    return _interface_fail(
        X, w, masses, sorted(t for t in topple), present[present.index(topple[0]) - 1]
    )


def _render_geometry(offsets, widths, masses):
    lines = []
    n = len(widths)
    lines.append(
        f"Block 1: width {widths[0]} unit(s), mass {masses[0]}, sitting on the ground."
    )
    for i in range(1, n):
        lines.append(
            f"Block {i + 1}: width {widths[i]} unit(s), mass {masses[i]}, "
            f"center shifted {offsets[i]:+d} unit(s) from the center of the block "
            f"directly below it."
        )
    return "\n".join(lines)


@dataclass
class TowerConfig(Config):
    n_min: int = 4
    n_max: int = 5
    width_hi: int = 10
    offset_hi: int = 2
    mass_lo: int = 1
    mass_hi: int = 3

    def apply_difficulty(self, level):
        self.n_min = 4 + level // 2
        self.n_max = 5 + level
        self.width_hi = 10 + level
        self.offset_hi = 2 + level
        self.mass_lo = 1
        self.mass_hi = 3 + level


class TowerBlockRemoval(Task):
    summary = ("Stacks of axis-aligned blocks with widths, masses, and offsets; "
               "removing or nudging one block forces upward overlap and center-of-mass "
               "support checks; answer is which blocks topple or shift and the height of "
               "the surviving stack.")
    design_choice = ("Represent block positions as integer grid coordinates and answer "
                     "with a sorted list of block IDs that topple, plus the final stack "
                     "height as an integer.")
    config_cls = TowerConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(4000):
            n = random.randint(cfg.n_min, cfg.n_max)
            widths = [random.choice(range(6, cfg.width_hi + 1, 2)) for _ in range(n)]
            masses = [random.randint(cfg.mass_lo, cfg.mass_hi) for _ in range(n)]
            offsets = [0] + [
                random.randint(-cfg.offset_hi, cfg.offset_hi) for _ in range(n - 1)
            ]
            X = [0] * n
            for i in range(1, n):
                X[i] = X[i - 1] + offsets[i]
            if _simulate(X, widths, masses, ('nudge', 0, 0), n)[0]:
                continue
            if random.random() < 0.5:
                remove_idx = random.randrange(n)
                action = ('remove', remove_idx)
            else:
                nudge_idx = random.randrange(n)
                delta = random.randint(-cfg.offset_hi, cfg.offset_hi)
                if delta == 0:
                    continue
                action = ('nudge', nudge_idx, delta)
            topple, survivors, X_after = _simulate(X, widths, masses, action, n)
            present = sorted([i for i in range(n) if action[0] != 'remove' or i != action[1]])
            if not _verify(X_after, widths, masses, present, topple):
                continue
            height = len(survivors)
            if height < 1:
                continue
            topple_ids = sorted(i + 1 for i in topple)
            topple_str = "none" if not topple_ids else ",".join(str(b) for b in topple_ids)
            answer = f"{topple_str} {height}"
            metadata = {
                "action": action,
                "n": n,
                "widths": widths,
                "masses": masses,
                "offsets": offsets,
                "positions": X,
                "topple": topple_ids,
                "height": height,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("tower_block_removal: failed to generate a valid example")

    def render_prompt(self, metadata):
        geometry = _render_geometry(
            metadata["offsets"], metadata["widths"], metadata["masses"]
        )
        action = metadata["action"]
        if action[0] == "remove":
            action_text = f"Remove block {action[1] + 1} entirely."
        else:
            action_text = (
                f"Nudge block {action[1] + 1}: shift its center by {action[2]:+d} "
                f"unit(s) horizontally."
            )
        return (
            "A tower of axis-aligned blocks rests on a flat, infinitely wide ground. "
            "A block occupies the horizontal interval centered on its center with "
            "half-width equal to half its width, and the ground supports the lowest "
            "block unconditionally.\n"
            f"{geometry}\n"
            "The middle/upper blocks must each support the center of mass of every "
            "block above them: the mass-weighted average center of the blocks strictly "
            f"above a block must lie strictly inside that block's footprint. {action_text} "
            "After the change, recompute the support at every interface below and above "
            "the change, from the bottom up; the lowest interface whose supported center "
            "of mass falls outside its footprint causes that block and every block above "
            "it to topple off the tower. Blocks that topple are removed; the others stay.\n"
            "Answer which block IDs (numbered 1 for the lowest block) topple, as a "
            "sorted comma-separated list with no spaces, or the single word 'none' if no "
            "block topples, followed by a space and the height (number of blocks) of the "
            "surviving stack as an integer. Example: '2,4 3' means blocks 2 and 4 "
            "topple and 3 blocks remain standing."
        )

    def score_answer(self, answer, entry):
        reference = str(entry["answer"]).strip()
        return 1.0 if str(answer).strip() == reference else 0.0
