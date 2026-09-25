"""Additive preference representability: can pairwise total comparisons among
multiattribute binary options be explained by positive latent attribute weights,
and is an unseen comparison then forced?

Design (assigned variant): each option is a binary vector over 5 attributes;
comparisons are pairwise totals. The solver checks existence of a positive
weight vector via linear feasibility and whether a specified unseen comparison
is implied by every consistent weight vector.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

try:
    import numpy as np
    from scipy.optimize import linprog
    _HAVE_SCIPY = True
except Exception:  # pragma: no cover
    _HAVE_SCIPY = False

_LABEL_CYCLE = ["feasible_not_forced", "feasible_and_forced", "infeasible"]
_label_count = 0


@dataclass
class AdditivePrefConfig(Config):
    n_attributes: int = 5
    n_options: int = 4

    def apply_difficulty(self, level):
        self.n_options = stochastic_rounding(3 + level)


def _feasible(attr_dim, comparisons):
    """True iff there exists w > 0 with sum_a w[a]*(i[a]-j[a]) > 0 for every
    comparison (i, j), where i, j are attribute vectors.

    The system is homogeneous and strict. w strictly satisfies all strict
    inequalities iff it satisfies A w >= 1 componentwise for some positive
    scaling (scale any strict solution up; conversely a solution to A w >= 1,
    w >= 1 is a strict solution). We solve that real linear program.

    Empty constraint set is trivially feasible.
    """
    if not comparisons:
        return True
    if not _HAVE_SCIPY:
        # fallback: tiny product enumeration over a normalized integer grid.
        from itertools import product
        B = 4
        for w0 in range(1, B + 1):
            for rest in product(range(1, B + 1), repeat=attr_dim - 1):
                w = (w0,) + rest
                if all(sum(w[a] * (i[a] - j[a]) for a in range(attr_dim)) > 0
                       for (i, j) in comparisons):
                    return True
        return False

    A = []
    for (i, j) in comparisons:
        A.append([i[a] - j[a] for a in range(attr_dim)])
    A = np.array(A, dtype=float)
    k = A.shape[1]
    # want A w >= 1  ->  -A w <= -1 ; and w >= 1
    A_ub = np.vstack([-A, -np.eye(k)])
    b_ub = np.concatenate([-np.ones(A.shape[0]), -np.ones(k)])
    res = linprog(np.zeros(k), A_ub=A_ub, b_ub=b_ub,
                  bounds=[(1.0, 1e6)] * k, method="highs")
    return res.status == 0


class AdditivePreferenceRepresentability(Task):
    summary = ("Translate pairwise total comparisons among binary 5-attribute "
               "options into constraints on positive latent attribute scores; "
               "decide whether additive preferences explain them and whether an "
               "unseen comparison is forced.")
    design_choice = ("Represent each option as a binary vector over a fixed set "
                     "of 5 attributes; comparisons are pairwise totals, and the "
                     "solver must check if a positive weight vector exists via "
                     "linear feasibility.")
    config_cls = AdditivePrefConfig

    def generate_entry(self):
        global _label_count
        k = self.config.n_attributes
        # enumerate the 31 nonzero binary vectors over the 5 attributes
        universe = [tuple((a >> b) & 1 for b in range(k)) for a in range(1, 1 << k)]
        assert len(universe) == 31, len(universe)
        n = self.config.n_options
        # round-robin over the three answers so every level stays balanced
        target = _LABEL_CYCLE[_label_count % 3]
        while True:
            options = random.sample(universe, n)
            if len(set(options)) != n:
                continue
            all_pairs = [(i, j) for i in range(n) for j in range(n) if i != j]
            n_comp = max(1, random.randrange(1, len(all_pairs) + 1))
            comparisons = random.sample(all_pairs, n_comp)

            # pick an unseen probe pair (a directed pair not already compared)
            seen = set(comparisons)
            unseen = [p for p in all_pairs if p not in seen]
            if not unseen:
                continue
            probe = random.choice(unseen)
            ip, jp = probe
            i_vec, j_vec = options[ip], options[jp]
            if i_vec == j_vec:
                continue

            # answer semantics: three-way label
            vec = lambda p: (options[p[0]], options[p[1]])
            base = _feasible(k, [vec(p) for p in comparisons])
            if not base:
                ans = "infeasible"
            else:
                rev_probe = (jp, ip)
                if _feasible(k, [vec(p) for p in comparisons + [rev_probe]]):
                    # retaining the reverse comparison stays feasible => the
                    # probe is NOT forced (both orders possible)
                    ans = "feasible_not_forced"
                elif _feasible(k, [vec(p) for p in comparisons + [probe]]):
                    # adding the probe stays feasible but its reverse does not
                    # => it is forced
                    ans = "feasible_and_forced"
                else:
                    # base feasible but adding probe infeasible: contradiction
                    # with base feasibility; reject this draw
                    continue

            if ans == target:
                _label_count += 1
                return Entry(metadata={
                    "options": options,
                    "comparisons": comparisons,
                    "probe": list(probe),
                }, answer=ans)

    def render_prompt(self, metadata):
        k = len(metadata["options"][0])
        options = metadata["options"]
        comparisons = metadata["comparisons"]
        probe = metadata["probe"]
        lines = []
        lines.append(
            "Five latent attributes are scored by unknown strictly positive "
            "weights; each option is a binary vector over the five attributes "
            "(1 = attribute present). The value of an option is the weighted "
            "sum of its attributes, and a person prefers option u to option v "
            "whenever u's weighted sum exceeds v's."
        )
        for i, o in enumerate(options):
            lines.append(f"Option {i} = {tuple(o)}")
        lines.append("Observed pairwise preferences (u > v means u preferred over v):")
        for (u, v) in comparisons:
            lines.append(f"  {u} > {v}")
        lines.append(
            f"Now the unseen comparison {probe[0]} > {probe[1]} is proposed. "
            "First decide whether there exists a strictly positive weight "
            "vector consistent with the observed preferences (an additive "
            "representation). Then decide the status of the proposed "
            "comparison among consistent weight vectors."
        )
        lines.append(
            "Answer exactly one of: 'infeasible' (no positive weight vector "
            "fits the observed preferences), 'feasible_not_forced' (a "
            f"consistent additive representation exists and {probe[0]} > "
            f"{probe[1]} holds for some but not all such representations), or "
            f"'feasible_and_forced' (a consistent additive representation "
            f"exists and {probe[0]} > {probe[1]} holds for every one)."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        k = len(entry.metadata["options"][0])
        options = entry.metadata["options"]
        comparisons = entry.metadata["comparisons"]
        probe = entry.metadata["probe"]
        vec = lambda p: (options[p[0]], options[p[1]])
        base = _feasible(k, [vec(p) for p in comparisons])
        if not base:
            gold = "infeasible"
        else:
            rev = (probe[1], probe[0])
            if _feasible(k, [vec(p) for p in comparisons + [rev]]):
                gold = "feasible_not_forced"
            else:
                gold = "feasible_and_forced"
        return 1.0 if str(answer).strip().lower() == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'additive_preference_representability (variant 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_latent_representation_r4/additive_preference_representability',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
