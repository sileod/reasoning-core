"""Schensted (row-insertion) tableau insertion task.

Insert a word's symbols one at a time into a row-sorted (row-increasing,
column-increasing) tableau, bumping the smallest larger entry down to the next
row on collision. The answer is the final row-sorted tableau encoded as a
semicolon-separated list of row strings with each row's entries comma-separated.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SchenstedConfig(Config):
    width: int = 4
    alphabet: int = 7

    def apply_difficulty(self, level):
        self.width = max(2, 3 + (level * 2) // 3)
        self.alphabet = 5 + level


def insert_symbol(tableau, symbol):
    """Iteratively row-insert `symbol` into `tableau` (list of sorted rows).

    Returns the new tableau. Standard Schensted bumping: in the first row find
    the smallest entry strictly greater than the incoming value and bump it to
    the next row; if none, append the value at the end of the row.
    """
    tableau = [list(row) for row in tableau]
    value = symbol
    for i in range(len(tableau) + 1):
        if i == len(tableau):
            tableau.append([])
        row = tableau[i]
        col = None
        for j, x in enumerate(row):
            if x > value:
                col = j
                break
        if col is None:
            row.append(value)
            break
        old = row[col]
        row[col] = value
        value = old
    return tableau


def encode_tableau(tableau):
    return ";".join(",".join(str(x) for x in row) for row in tableau)


def check_shape(tableau):
    """Return True if lengths are weakly decreasing (a valid Young shape)."""
    return all(len(tableau[i]) >= len(tableau[i + 1]) for i in range(len(tableau) - 1))


def verify_tableau(tableau):
    """Independent verification: rows weakly increasing, columns strictly increasing."""
    for row in tableau:
        for a, b in zip(row, row[1:]):
            if a > b:
                return False
    for c in range(max((len(r) for r in tableau), default=0)):
        col = [r[c] for r in tableau if c < len(r)]
        for a, b in zip(col, col[1:]):
            if a >= b:
                return False
    return True


class SchenstedTableauInsertion(Task):
    summary = "Insert a word's symbols one at a time into a row-sorted tableau, bumping the smallest larger entry down to the next row on collision; answers are the final tableau rows or a single insertion's bump path."
    design_choice = "Answer as the final row-sorted tableau encoded as a semicolon-separated list of row strings, with each row's entries comma-separated."

    config_cls = SchenstedConfig

    def generate_entry(self):
        width = self.config.width
        alphabet = self.config.alphabet
        while True:
            word = [random.randint(1, alphabet) for _ in range(width)]
            tableau = []
            for s in word:
                tableau = insert_symbol(tableau, s)
            if not check_shape(tableau):
                continue
            assert verify_tableau(tableau), "insertion produced invalid tableau"
            assert encode_tableau(tableau) is not None
            break
        return Entry(
            metadata={"word": word, "alphabet": alphabet, "tableau": encode_tableau(tableau)},
            answer=encode_tableau(tableau),
        )

    def render_prompt(self, metadata):
        word = ", ".join(str(x) for x in metadata["word"])
        return (
            f"Starting from an empty tableau, insert the symbols {word} one at a "
            f"time in order using Schensted row insertion: in each row, the inserted "
            f"value bumps the smallest entry strictly greater than it down to the next "
            f"row (which then repeats the process); if no row entry is greater, the "
            f"value is appended at the end of the row. Give the final row-sorted "
            f"tableau as semicolon-separated rows, each row's entries comma-separated, "
            f"top row first. For example, the tableau with rows [1,3] then [2] is "
            f"written \"1,3;2\"."
        )

    def score_answer(self, answer, entry):
        try:
            answer = answer.strip()
        except Exception:
            return 0.0
        return 1.0 if answer == entry.metadata["tableau"] else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'schensted_tableau_insertion (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_novel_composition_r1/schensted_tableau_insertion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
