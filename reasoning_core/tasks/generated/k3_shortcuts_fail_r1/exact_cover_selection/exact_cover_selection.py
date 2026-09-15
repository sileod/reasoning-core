"""Exact cover selection: choose a subfamily of labeled subsets that covers
every element of a fixed ordered universe exactly once, or report NONE."""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ExactCoverSelectionV1Config(Config):
    universe_size: int = 6
    n_subsets: int = 8
    solvable_rate: float = 0.65

    def apply_difficulty(self, level):
        self.universe_size = stochastic_rounding(self.universe_size + 2 * level)
        self.n_subsets = stochastic_rounding(self.n_subsets + 3 * level)


def _gen_subset(universe_size):
    """Return one nonempty subset of the universe as a sorted tuple."""
    k = random.randint(1, universe_size)
    return tuple(sorted(random.sample(range(universe_size), k)))


def _all_covers(subsets, universe_size):
    """Enumerate ALL exact covers as sorted tuples of row indices.

    Algorithm-X style: repeatedly choose the uncovered element with the fewest
    disjoint candidate rows and branch on each, so the search is fast and the
    results are collected completely for the sizes we generate."""
    n = len(subsets)
    sets = [set(s) for s in subsets]
    row_of = {e: [i for i in range(n) if e in sets[i]]
              for e in range(universe_size)}
    results = []

    def rec(covered, chosen):
        if len(covered) == universe_size:
            results.append(tuple(sorted(chosen)))
            return
        missing = [e for e in range(universe_size) if e not in covered]
        e = min(missing, key=lambda x: len(row_of[x]))
        for i in row_of[e]:
            if i in chosen:
                continue
            s = sets[i]
            if covered & s:
                continue
            rec(covered | s, chosen | {i})

    rec(frozenset(), frozenset())
    return results


def _plant_partition(universe_size, n_subsets):
    """Build rows whose first several rows partition the universe; the rest are
    arbitrary nonempty subsets. Returns the full row list."""
    universe = list(range(universe_size))
    random.shuffle(universe)
    p = random.randint(1, min(n_subsets, universe_size))
    cuts = sorted(random.sample(range(1, universe_size), p - 1)) if p > 1 else []
    rows = []
    prev = 0
    for c in cuts + [universe_size]:
        rows.append(tuple(sorted(universe[prev:c])))
        prev = c
    while len(rows) < n_subsets:
        rows.append(_gen_subset(universe_size))
    return rows


def _make_solvable(universe_size, n_subsets):
    """Build an instance guaranteed solvable; return (subsets, expected_answer)
    where expected_answer is the lexicographically smallest exact cover."""
    for _ in range(40):
        subsets = _plant_partition(universe_size, n_subsets)
        covers = _all_covers(subsets, universe_size)
        if covers:
            best = min(covers, key=tuple)
            return subsets, list(best)
    raise RuntimeError("could not build solvable instance")


def _make_unsolvable(universe_size, n_subsets):
    """Build an instance guaranteed to have no exact cover; return subsets."""
    for _ in range(60):
        base = _plant_partition(universe_size, n_subsets)
        # drop the first element of row 0
        row0 = list(base[0])
        if len(row0) < 2:
            continue
        removed = row0.pop(0)
        subsets = [tuple(row0)] + list(base[1:])
        if not _all_covers(subsets, universe_size):
            return subsets
    # fallback: pure random rows until one has no cover
    for _ in range(200):
        subsets = [_gen_subset(universe_size) for _ in range(n_subsets)]
        if not _all_covers(subsets, universe_size):
            return subsets
    raise RuntimeError("could not build unsolvable instance")


class ExactCoverSelection(Task):
    summary = (
        "Select a subfamily of labeled overlapping subsets covering every element "
        "of the universe exactly once, or report NONE; vary universe size, subset "
        "shapes, planted solutions; answer is the sorted chosen labels."
    )
    design_choice = (
        "Implement instances as a 0-1 matrix with a fixed element order; answers "
        "are sorted column indices of chosen rows, with row labels as consecutive "
        "integers."
    )
    config_cls = ExactCoverSelectionV1Config

    def generate_entry(self):
        universe_size = self.config.universe_size
        n_subsets = self.config.n_subsets
        solvable = random.random() < self.config.solvable_rate
        if solvable:
            subsets, expected = _make_solvable(universe_size, n_subsets)
            covers = _all_covers(subsets, universe_size)
            best = min(covers, key=tuple)
            assert sorted(expected) == list(best)
            answer = ",".join(str(i) for i in best)
        else:
            subsets = _make_unsolvable(universe_size, n_subsets)
            assert len(_all_covers(subsets, universe_size)) == 0
            answer = "NONE"
        metadata = {"universe_size": int(universe_size),
                    "n_subsets": int(n_subsets),
                    "universe": list(range(universe_size)),
                    "subsets": [list(s) for s in subsets],
                    "solvable": solvable}
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        universe = list(range(metadata["universe_size"]))
        lines = [
            f"The universe U has fixed order {universe}. The following labeled "
            "subsets (the label is the row index) are given:"
        ]
        for i, s in enumerate(metadata["subsets"]):
            lines.append(f"  row {i}: {s}")
        lines.append(
            "Choose a subfamily of rows that covers every element of U exactly once "
            "(an exact cover). If more than one exact cover exists, pick the one "
            "whose sorted row labels are lexicographically smallest. "
            "Answer with the chosen row labels in sorted order, comma-separated "
            "(e.g. '1,3,5'), or the single word NONE if no exact cover exists."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        raw = answer.strip()
        n = entry.metadata["n_subsets"]
        universe = set(range(entry.metadata["universe_size"]))
        subsets = [set(s) for s in entry.metadata["subsets"]]
        covers = _all_covers(entry.metadata["subsets"],
                             entry.metadata["universe_size"])
        if raw.upper() == "NONE":
            return 1.0 if not covers else 0.0
        try:
            chosen = [int(tok) for tok in raw.split(",")]
        except (ValueError, AttributeError):
            return 0.0
        if not chosen or len(set(chosen)) != len(chosen):
            return 0.0
        if any(i < 0 or i >= n for i in chosen):
            return 0.0
        covered = set()
        for i in chosen:
            covered |= subsets[i]
        if covered != universe:
            return 0.0
        if not covers:
            return 0.0
        best = min(covers, key=tuple)
        return 1.0 if sorted(chosen) == sorted(best) else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'exact_cover_selection (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/exact_cover_selection',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
