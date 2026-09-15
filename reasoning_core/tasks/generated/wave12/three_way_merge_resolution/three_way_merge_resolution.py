"""Three-way merge resolution task.

Given a base sequence of lines and independently edited left/right variants,
determine whether both authors edited a given line (a conflict) or only one did.
Return the merged sequence as a canonical string, bracketing conflicted lines as
'triples <left>|<base>|<right>'.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


def _render(merged_lines):
    parts = []
    for line in merged_lines:
        if isinstance(line, (tuple, list)):
            parts.append("<%s|%s|%s>" % (line[0], line[1], line[2]))
        else:
            parts.append(str(line))
    return "\n".join(parts)


def _parse_answer(answer):
    """Parse a canonical answer back into a list of tokens and conflict triples."""
    if not isinstance(answer, str):
        return None
    lines = []
    for raw in answer.split("\n"):
        raw = raw.rstrip("\n")
        if raw.startswith("<") and raw.endswith(">"):
            inner = raw[1:-1]
            parts = inner.split("|")
            if len(parts) != 3:
                return None
            lines.append(tuple(parts))
        else:
            lines.append(raw)
    return lines


def _score_answer(answer, entry):
    if _parse_answer(answer) is None:
        return 0.0
    return 1.0 if answer == entry.answer else 0.0


@dataclass
class MergeConfig(Config):
    base_len: int = 4
    edit_rate: float = 0.4

    def apply_difficulty(self, level):
        self.base_len = stochastic_rounding(self.base_len + level)
        self.edit_rate = min(0.7, 0.4 + 0.05 * level)


class ThreeWayMergeResolution(Task):
    summary = (
        "Perform deterministic base, left, and right sequence merging, "
        "distinguishing independent edits from conflicts and returning merged "
        "text or conflict spans."
    )
    design_choice = (
        "Answer format: return a canonical string listing merged text lines, "
        "with conflict spans as bracketed triples 'left|base|right'"
    )
    config_cls = MergeConfig

    def generate_entry(self):
        n = self.config.base_len
        base = [random.choice("abcdefgh") for _ in range(n)]

        left = list(base)
        right = list(base)
        for i in range(n):
            if random.random() < self.config.edit_rate:
                left[i] = random.choice("ABCDEFGH")
            if random.random() < self.config.edit_rate:
                right[i] = random.choice("WXYZ")

        merged = []
        has_conflict = False
        for i in range(n):
            a, b, orig = left[i], right[i], base[i]
            if a == b and a == orig:
                merged.append(orig)
            elif a == orig:
                merged.append(b)
            elif b == orig:
                merged.append(a)
            else:
                merged.append((a, orig, b))
                has_conflict = True

        answer = _render(merged)
        return Entry(metadata={"base": list(base), "left": list(left),
                               "right": list(right),
                               "has_conflict": has_conflict},
                     answer=answer)

    def render_prompt(self, metadata):
        rows = []
        for i in range(len(metadata["base"])):
            rows.append(
                "index %d, base %s, left %s, right %s"
                % (i, metadata["base"][i], metadata["left"][i],
                   metadata["right"][i])
            )
        return (
            "Three-way merge. The base version has lines with these contents "
            "(showing base, left-author edit, then right-author edit per "
            "line):\n"
            + "\n".join(rows)
            + "\nMerge the two edits line by line. A line both authors changed "
            "to different values is a conflict: emit it as a bracketed triple "
            "<left|base|right>. A line only one author changed takes that "
            "author's new content. A line nobody changed keeps its base "
            "content. Return one merged output line per base index, in "
            "ascending index order, joined by newlines."
        )

    def score_answer(self, answer, entry):
        return _score_answer(answer, entry)


TASK_META = {'parent_source_id': None,
 'idea': 'three_way_merge_resolution (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:three_way_merge_resolution',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/three_way_merge_resolution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1602009423,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
