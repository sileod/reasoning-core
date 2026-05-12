# reasoning_core/tasks/complexity.py
"""
Complexity classification task.

Given a Python program, predict its asymptotic time complexity class
from among: O(1) / O(log n) / O(n) / O(n log n) / O(n^2).

Generation uses slot-filled templates with declared complexity by
construction. Each instantiated program is profiled with an op-counting
oracle; mismatched programs are rejected before they become problems.
"""

import random
from dataclasses import dataclass
from easydict import EasyDict as edict

from reasoning_core.template import Task, Problem, Config

from ._gramforge_helpers.complexity_utils.complexity_templates import (
    LABELS, templates_by_label,
)
from ._gramforge_helpers.complexity_utils.slot_filler import SlotFiller
from ._gramforge_helpers.complexity_utils.profiler import ComplexityProfiler
from ._gramforge_helpers.complexity_utils.big_o_validator import BigOValidator


# ── Label progression by level ────────────────────────────────────────────────
# Easiest three are distinguishable without tracking inner-loop behavior;
# adding log and n-log-n requires reasoning about divide-by-2 patterns.
_LABEL_PROGRESSION = [
    'O(1)', 'O(n)', 'O(n^2)', 'O(log n)', 'O(n log n)',
]


@dataclass
class ComplexityConfig(Config):
    active_labels_count: int = 2
    require_consensus: bool = False
    run_big_o: bool = False

    def update(self, c):
        self.active_labels_count = min(5, self.active_labels_count + int(c))


def _normalize_label(s: str) -> str:
    """Normalize a complexity label for comparison: strip, lowercase, drop spaces."""
    return str(s).strip().lower().replace(' ', '')


class Complexity(Task):
    task_name = "complexity"

    # Conservative ratio works for 2–5 active labels without starving any class
    balancing_key_ratio = 0.35

    def __init__(self, config=None):
        super().__init__(config=config if config is not None else ComplexityConfig())
        self._profiler = ComplexityProfiler(entry_point='solve')
        self._validator = BigOValidator()
        self._filler = SlotFiller()

    # ── Generation ────────────────────────────────────────────────────────

    def _active_labels(self) -> list:
        k = max(2, min(5, self.config.active_labels_count))
        return _LABEL_PROGRESSION[:k]

    def generate(self) -> Problem:
        active = self._active_labels()

        # Try up to N times to produce a valid record. Failures come from
        # slot-fill errors, profiler mismatches, or (rare) execution errors.
        for _ in range(200):
            label = random.choice(active)
            candidates = templates_by_label(label)
            if not candidates:
                continue
            tpl = random.choice(candidates)

            try:
                fills = self._filler.fill_template(tpl)
                code = tpl.instantiate(fills)
            except Exception:
                continue

            try:
                profile = self._profiler.profile(code)
            except Exception:
                continue

            if profile.label != tpl.label:
                continue

            # big_O cross-check (opt-in)
            if self.config.run_big_o:
                big_o_label = self._validator.classify(code, entry=tpl.entry)
            else:
                big_o_label = 'unavailable'

            if big_o_label in ('unavailable', 'error', 'other'):
                agree = False
            else:
                agree = (big_o_label == profile.label)

            if self.config.require_consensus and not agree:
                continue

            # Assemble the MC choices (4 labels: correct + 3 distractors
            # drawn from active labels when possible, else all labels).
            pool = active if len(active) >= 4 else LABELS
            others = [lbl for lbl in pool if lbl != tpl.label]
            random.shuffle(others)
            distractors = others[:3]
            # Pad with unused labels if active set is too small
            if len(distractors) < 3:
                extras = [lbl for lbl in LABELS if lbl != tpl.label and lbl not in distractors]
                random.shuffle(extras)
                distractors += extras[: 3 - len(distractors)]

            choices = [tpl.label] + distractors
            random.shuffle(choices)
            correct_index = choices.index(tpl.label)

            metadata = edict(
                code=code,
                choices=choices,
                correct_index=correct_index,
                label=tpl.label,
                template_name=tpl.name,
                template_label=tpl.label,
                profiler_label=profile.label,
                profiler_slope=profile.slope,
                profiler_r_squared=profile.r_squared,
                profiler_counts={str(k): v for k, v in dict(profile.counts).items()},
                big_o_label=big_o_label,
                labels_agree=agree,
                slot_fills=dict(fills),
                active_labels=list(active),
            )
            return Problem(metadata=metadata, answer=tpl.label)

        raise RuntimeError(
            f"Complexity: failed to generate valid record after 200 attempts "
            f"(active_labels={active})"
        )

    # ── Prompt ────────────────────────────────────────────────────────────

    def prompt(self, metadata) -> str:
        choices_text = '\n'.join(f"  - {c}" for c in metadata.choices)
        return (
            f"What is the asymptotic time complexity of the following Python "
            f"function as a function of `n`?\n\n"
            f"```python\n{metadata.code}\n```\n\n"
            f"Choose exactly one of the following:\n"
            f"{choices_text}\n\n"
            f"Answer with the complexity class only (e.g. `O(n)`)."
        )

    # ── Scoring (must not use self) ───────────────────────────────────────

    def score_answer(self, answer, entry):
        reference = entry['answer']
        if answer is None:
            return 0
        if _normalize_label(answer) == _normalize_label(reference):
            return 1
        return 0

    # ── Balancing ─────────────────────────────────────────────────────────

    def balancing_key(self, problem):
        return str(problem.answer)
