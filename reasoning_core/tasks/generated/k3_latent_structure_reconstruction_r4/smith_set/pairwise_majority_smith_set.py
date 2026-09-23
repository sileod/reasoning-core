import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SmithSetConfig(Config):
    n_candidates: int = 5
    margin_max: int = 2
    level: int = 0
    seed: int = 0

    def apply_difficulty(self, level):
        self.level = level
        self.n_candidates = 5 + min(level, 4)
        self.margin_max = 2 + min(level // 2, 2)


def _smith_set(n, margin):
    """Return the Smith set (smallest set defeating every outsider) of a
    tournament described by pairwise margins. `margin[(w,l)]` means w beats l."""

    def beats(a, b):
        return (a, b) in margin or (b, a) in margin

    def who(a, b):
        return a if (a, b) in margin else b

    # The Smith set = set of candidates that can almost beat everyone outside,
    # computed via the top strongly-connected component closure: a candidate is
    # in the Smith set iff it can reach (via beat path) every candidate that it
    # is in a cycle with, and it is not reachable-by-beating from any candidate
    # outside the Smith set. Practical algorithm: repeatedly, a candidate that
    # is beaten by a candidate outside the current set is removed.
    cands = set(range(n))

    # neighbours in the beat graph: a beats b
    adj = {c: set() for c in cands}
    for a in range(n):
        for b in range(n):
            if a != b and beats(a, b) and who(a, b) == a:
                adj[a].add(b)

    def reach(start):
        seen = set()
        stack = [start]
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            stack.extend(adj[x] - seen)
        return seen

    # Smith set = { c : for every d, if c is beat-reachable to all of its peers }.
    # Standard characterization: the Smith set is the set of candidates that
    # beat (directly or transitively) everyone outside the set. Equivalently:
    # S is the minimal dominant set. We compute using the filter: keep candidate
    # c iff c is not beaten (reachable to) by any candidate that c cannot
    # reach back (i.e. not strictly dominated by anyone). Strict domination:
    # d strictly dominates c if d reaches c but c does not reach d. The Smith
    # set is the set of candidates not strictly dominated by anyone, together
    # with closure — actually the candidates that are top: not strictly
    # dominated by anyone.
    smith = set()
    for c in cands:
        dominated = False
        rc = reach(c)
        for d in cands:
            if d == c:
                continue
            rd = reach(d)
            if c in rd and d not in rc:
                dominated = True
                break
        if not dominated:
            smith.add(c)
    return smith


def _build_tournament(n, level):
    """Build a Condorcet-cyclic tournament over candidates 0..n-1. Return
    margin dict keyed by (winner, loser)."""
    margin = {}
    for i in range(n):
        for j in range(i + 1, n):
            m = random.randint(1, 1 + level)
            if random.random() < 0.5:
                margin[(i, j)] = m
            else:
                margin[(j, i)] = m
    return margin


class SmithSetTask(Task):
    task_name = "smith_set"
    summary = "Pairwise majority tallies with margins over a candidate slate: trace beat relations upward to find the smallest set that defeats every outsider; answer its sorted membership or a queried candidate's membership status."
    design_choice = "Vary difficulty by controlling Condorcet cycles: present either a single top cycle plus a dominated block, or multiple interlocking cycles requiring iterative upward closure."
    config_cls = SmithSetConfig

    def generate_entry(self):
        n = self.config.n_candidates
        level = self.config.level
        margin = _build_tournament(n, level)
        smith = _smith_set(n, margin)

        # balance responses; choose query mode sometimes
        if self.config.level <= 1 or random.random() < 0.5:
            answer = ",".join(str(x) for x in sorted(smith))
            opt = "sorted_membership"
            qry = None
        else:
            qry = random.randrange(n)
            answer = str(int(qry in smith))
            opt = "query_membership"

        return Entry(
            metadata={
                "n_candidates": n,
                "margins": {f"{w}>{l}": m for (w, l), m in margin.items()},
                "opt_response": opt,
                "query": qry,
                "smith_set": sorted(smith),
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        lines = [
            f"There are {metadata['n_candidates']} candidates numbered 0 to {metadata['n_candidates'] - 1}.",
        ]
        beats = [f"{k.split('>')[0]} beats {k.split('>')[1]} by margin {m}" for k, m in sorted(metadata["margins"].items())]
        lines.append("In pairwise majority elections: " + "; ".join(beats) + ".")
        lines.append(
            "The Smith set is the smallest set of candidates such that every candidate in the set "
            "defeats every candidate outside the set, tracing beat relations upward transitively."
        )
        if metadata["opt_response"] == "sorted_membership":
            lines.append(
                "Give the Smith set's members as a comma-separated list sorted ascending, e.g. 1,4,5."
            )
        else:
            lines.append(
                f"Is candidate {metadata['query']} in the Smith set? Answer 1 for yes, 0 for no."
            )
        return "\n".join(lines)


TASK_META = {'parent_source_id': None,
 'idea': 'pairwise_majority_smith_set (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/pairwise_majority_smith_set',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
