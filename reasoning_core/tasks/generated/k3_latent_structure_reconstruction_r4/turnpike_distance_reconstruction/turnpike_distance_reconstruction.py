import random
from collections import Counter
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class TurnpikeConfig(Config):
    n_points: int = 5
    coord_max: int = 25

    def apply_difficulty(self, level):
        self.n_points = random.randint(4 + level, 6 + 2 * level)
        self.coord_max = 20 * (1 + level)


def _reconstruct(distances, max_nodes=40000):
    """Return the canonical lexicographically smallest sorted placement of points
    on a line whose pairwise distances give `distances`, or None if infeasible.

    Classic turnpike / partial-digest backtracking: the largest remaining
    distance must connect an extreme, so it pins a candidate at `d` or `D - d`.
    All valid placements are enumerated and the lexicographically smallest
    sorted coordinate tuple is returned.
    """
    D = max(distances)
    remaining = Counter(distances)
    remaining[D] -= 1
    if remaining[D] == 0:
        del remaining[D]
    pts = [0, D]
    best = None
    nodes = [0]

    def _feasible(cand):
        out = []
        for p in pts:
            dx = abs(cand - p)
            if remaining.get(dx, 0) <= 0:
                return None
            out.append(dx)
        return out

    def _search():
        nonlocal best
        nodes[0] += 1
        if nodes[0] > max_nodes:
            raise RuntimeError("search too deep")
        if not remaining:
            cand_sol = tuple(sorted(pts))
            if best is None or cand_sol < best:
                best = cand_sol
            return True
        d = max(remaining)
        found = False
        for cand in (d, D - d):
            need = _feasible(cand)
            if need is None:
                continue
            for dx in need:
                remaining[dx] -= 1
                if remaining[dx] == 0:
                    del remaining[dx]
            pts.append(cand)
            if _search():
                found = True
            pts.pop()
            for dx in need:
                remaining[dx] = remaining.get(dx, 0) + 1
        return found

    try:
        if not _search():
            return None
    except RuntimeError:
        return None
    return list(best)


class TurnpikeDistanceReconstruction(Task):
    summary = "Recover points on a line from the multiset of all pairwise distances by recursively assigning the largest remaining gap to an end; answer the canonical lexicographically smallest placement."
    design_choice = "Answer format: return the canonical left-to-right sorted coordinate list as a single string of space-separated integers, with ties broken by choosing the lexicographically smallest placement."
    task_version = 2
    config_cls = TurnpikeConfig

    def generate_entry(self):
        n = self.config.n_points
        cmax = self.config.coord_max
        while True:
            pts = sorted(random.sample(range(cmax), n))
            distances = [
                pts[j] - pts[i]
                for i in range(n)
                for j in range(i + 1, n)
            ]
            canon = _reconstruct(distances)
            if canon is None:
                continue
            assert sorted(
                canon[j] - canon[i]
                for i in range(len(canon))
                for j in range(i + 1, len(canon))
            ) == sorted(distances), "canonical placement must reproduce the distance multiset"
            answer = " ".join(str(x) for x in canon)
            return Entry(
                metadata={
                    "points": pts,
                    "distances": sorted(distances),
                },
                answer=answer,
            )

    def render_prompt(self, metadata):
        dist = " ".join(str(d) for d in metadata["distances"])
        return (
            "A set of points lies on a line. The multiset of all pairwise "
            "distances between them is:\n"
            f"{dist}\n"
            "Recover the coordinates of the points by the classical turnpike "
            "(partial digest) method: repeatedly place the largest remaining "
            "distance at one of the two ends. Give your answer as a single "
            "left-to-right sorted list of integer coordinates separated by "
            "spaces. If several placements are valid, give the "
            "lexicographically smallest sorted list."
        )


TASK_META = {'parent_source_id': None,
 'idea': 'turnpike_distance_reconstruction (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/turnpike_distance_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
