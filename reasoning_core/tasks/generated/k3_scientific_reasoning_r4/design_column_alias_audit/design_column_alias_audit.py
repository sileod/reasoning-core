"""Design column alias audit: sign-coded 2-level design matrix inner products.

A run sheet is a design matrix whose rows are experiments and whose columns are
main effects (2-level, encoded as +/-1) plus interactions built as products of
main-effect columns. Two columns are aliased (fully confounded) when they are
proportional, i.e. |inner product| over the runs equals the number of runs.

The task: given a run sheet, report every aliased pair among the main-effect and
interaction columns as canonical strings 'A-BC,D-AB' sorted lexicographically, or
'none' if no pair is aliased.
"""

import random
from dataclasses import dataclass
from itertools import combinations
from typing import List, Tuple

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'design_column_alias_audit (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scientific_reasoning_r4/design_column_alias_audit',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Generate run sheets with 2-level factors and present the "
                 "confounded pairs as canonical strings like 'A-BC,D-AB' sorted "
                 "lexicographically, with a 'none' verdict for orthogonal designs.")

_COLS = ['A', 'B', 'C', 'D', 'E', 'F']


def _interaction_name(parts: Tuple[str, ...]) -> str:
    return ''.join(sorted(parts))


def _canon(a, b):
    """Canonicalize an aliased pair as 'A-BC' with lexicographically smaller name first."""
    if a < b:
        return a + '-' + b
    return b + '-' + a


def build_prompt(metadata):
    fac = ', '.join(metadata['factors'])
    n_rows = metadata['n_rows']
    runs = '\n'.join(
        '  '.join('+' + metadata['factors'][i] if row[i] == 1
                  else '-' + metadata['factors'][i]
                  for i in range(len(metadata['factors'])))
        for row in metadata['design']
    )
    return (
        f"Each listed line is one experiment in a 2-level factorial design. Every "
        f"factor column is sign-coded +1/-1 (written +F / -F). An interaction "
        f"column such as AB or ABC is the column-wise product of its member factor "
        f"columns, so its sign in each run is the product of the corresponding "
        f"factor signs. Two columns are aliased (fully confounded) precisely when "
        f"they are proportional, equivalently when their inner product over the "
        f"{n_rows} runs has magnitude equal to the number of runs {n_rows} "
        f"(correlation magnitude 1). List every aliased pair among the main-effect "
        f"and interaction columns, each as the two column names joined by '-' with "
        f"the lexicographically smaller name first, all pairs sorted "
        f"lexicographically and joined by ','; answer 'none' if no pair is "
        f"aliased.\n\n"
        f"Factors: {fac}\n"
        f"Runs:\n{runs}"
    )


def _parse_answer(answer, columns):
    """Parse a candidate answer into a frozenset of pairs, or None if malformed.

    'none' (case-insensitive) means no pairs (frozenset()). Any segment that is
    not exactly two distinct column names joined by '-' makes the whole answer
    invalid (returns None) so it can never score.
    """
    if answer is None:
        return None
    s = str(answer).strip()
    if s == '':
        return None
    if s.lower() == 'none':
        return frozenset()
    result = set()
    for pair in s.split(','):
        pair = pair.strip()
        if not pair:
            return None
        parts = pair.split('-')
        if len(parts) != 2:
            return None
        a, b = parts[0].strip(), parts[1].strip()
        if a == b or a not in columns or b not in columns:
            return None
        result.add(frozenset((a, b)))
    return frozenset(result)


@dataclass
class DesignColumnAliasAuditConfig(Config):
    n_factors: int = 3
    n_rows: int = 4
    n_interactions: int = 1

    def apply_difficulty(self, level):
        self.n_factors = stochastic_rounding(self.n_factors + level)
        self.n_rows = stochastic_rounding(self.n_rows + 2 * level)
        self.n_interactions = stochastic_rounding(self.n_interactions + level)


class DesignColumnAliasAudit(Task):
    summary = ("Audit each run sheet as a sign-coded design matrix: inner products "
               "among main-effect and interaction columns across experiments expose "
               "aliasing; answer the confounded-pair list or the orthogonality "
               "verdict.")
    config_cls = DesignColumnAliasAuditConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n_factors = min(int(cfg.n_factors), len(_COLS))
        n_interactions = int(cfg.n_interactions)
        max_possible_interactions = (1 << n_factors) - 1 - n_factors
        n_interactions = min(n_interactions, max(0, max_possible_interactions))
        n_rows = max(int(cfg.n_rows), 2)
        force_prob = 0.78

        factors = _COLS[:n_factors]

        for _attempt in range(400):
            possible = []
            for r in range(2, n_factors + 1):
                for comb in combinations(factors, r):
                    possible.append(tuple(comb))
            random.shuffle(possible)
            interactions = possible[:n_interactions]
            force_target = None
            if interactions and random.random() < force_prob:
                pivot_int = interactions[random.randrange(len(interactions))]
                other = [f for f in factors if f not in pivot_int]
                if other:
                    force_target = (pivot_int, random.choice(other))

            # random free factor columns
            factor_cols = {f: [random.choice([-1, 1]) for _ in range(n_rows)]
                           for f in factors}

            if force_target is not None:
                pivot_int, xfac = force_target
                others = [f for f in pivot_int if f != xfac]
                if len(pivot_int) >= 2 and len(others) == len(pivot_int):
                    # X is chosen outside pivot_int, so pivot_int fully free
                    pass
                # redefine a pivot factor so that pivot_int column = c * X column
                pivot = pivot_int[0]
                prod_others = [1] * n_rows
                for f in pivot_int[1:]:
                    for i in range(n_rows):
                        prod_others[i] *= factor_cols[f][i]
                c = random.choice([-1, 1])
                xcol = factor_cols[xfac]
                factor_cols[pivot] = [c * prod_others[i] * xcol[i]
                                      for i in range(n_rows)]

            cols = list(factors) + [_interaction_name(p) for p in interactions]
            col_signs = []
            for col in cols:
                if len(col) == 1:
                    col_signs.append(factor_cols[col])
                else:
                    vec = [1] * n_rows
                    for ch in col:
                        for i in range(n_rows):
                            vec[i] *= factor_cols[ch][i]
                    col_signs.append(vec)

            pairs = set()
            for i, j in combinations(range(len(cols)), 2):
                ip = sum(a * b for a, b in zip(col_signs[i], col_signs[j]))
                if abs(ip) == n_rows:
                    pairs.add(_canon(cols[i], cols[j]))
            pairs = sorted(pairs)

            answer = ','.join(pairs) if pairs else 'none'

            design = [[factor_cols[f][r] for f in factors] for r in range(n_rows)]
            return Entry(
                metadata={
                    'factors': list(factors),
                    'design': design,
                    'columns': cols,
                    'n_rows': n_rows,
                },
                answer=answer,
            )

        raise RuntimeError('design_column_alias_audit: failed to build run sheet')

    def render_prompt(self, metadata):
        return build_prompt(metadata)

    def score_answer(self, answer, entry):
        columns = entry.metadata['columns']
        gold = entry.answer
        gold_pairs = frozenset() if gold == 'none' else frozenset(
            frozenset(p.split('-')) for p in gold.split(','))
        parsed = _parse_answer(answer, columns)
        if parsed is None:
            return 0.0
        return 1.0 if parsed == gold_pairs else 0.0
