import ast
import json
import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ResidualSymmetryConfig(Config):
    max_vertices: int = 9
    max_pinned: int = 3

    def apply_difficulty(self, level):
        self.max_vertices = stochastic_rounding(9 + level * 2)
        self.max_pinned = stochastic_rounding(3 + level)


def _group_elements(m):
    elems = []
    for d in range(m):
        elems.append(tuple((k + d) % m for k in range(m)))
        elems.append(tuple((d - k) % m for k in range(m)))
    return elems


def _pointwise_fix(elems, pinned):
    pinned = tuple(pinned)
    return [e for e in elems if all(e[p] == p for p in pinned)]


def _orbits(elems, m):
    parent = list(range(m))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for e in elems:
        for k in range(m):
            union(k, e[k])

    blocks = {}
    for k in range(m):
        blocks.setdefault(find(k), []).append(k)
    orbit_blocks = [sorted(b) for b in blocks.values()]
    orbit_blocks.sort(key=lambda b: b[0])
    return orbit_blocks


def _parse_blocks(text):
    try:
        val = ast.literal_eval(str(text).strip())
    except Exception:
        return None
    if not isinstance(val, list):
        return None
    blocks = []
    for b in val:
        if not isinstance(b, list) or not all(isinstance(x, int) for x in b):
            return None
        blocks.append(b)
    blocks = [sorted(b) for b in blocks]
    blocks.sort(key=lambda x: (x[0] if x else 0))
    return blocks


class ResidualSymmetryUnderPinning(Task):
    summary = ("Intervene on finite symmetric structures using fixed sites, distinct labels or "
               "interchangeable marked sets; retain exactly the transformations respecting the "
               "intervention and report the resulting orbit partition.")
    config_cls = ResidualSymmetryConfig
    design_choice = ("Instances present a finite set with a fixed marked subset; solvers output "
                     "the orbit partition of the subgroup fixing that subset pointwise, with "
                     "labels as distinct integers.")

    def generate_entry(self):
        m = random.randint(4, self.config.max_vertices)
        max_p = min(self.config.max_pinned, m - 1)
        candidates = list(range(max_p + 1))
        weights = [max(1, (max_p - i)) for i in candidates]
        pinned_count = random.choices(candidates, weights=weights)[0]
        pinned = sorted(random.sample(range(m), pinned_count))
        elems = _group_elements(m)
        fixed = _pointwise_fix(elems, pinned)
        orbit_blocks = _orbits(fixed, m)
        flat = [x for b in orbit_blocks for x in b]
        assert sorted(flat) == list(range(m)), "orbit partition must cover the vertex set exactly"
        answer = json.dumps(orbit_blocks)
        return Entry(metadata={"m": m, "pinned": pinned, "orbit_blocks": orbit_blocks},
                     answer=answer)

    def render_prompt(self, metadata):
        m = metadata["m"]
        pinned = metadata["pinned"]
        if len(pinned) == 0:
            marked = "no vertices are marked (the marked set is empty), so every symmetry is kept"
        else:
            marked = ("the marked vertices %s are fixed pointwise, so we keep only the "
                      "symmetries that map each one to itself" % (pinned,))
        return (
            "Consider the dihedral group D_%d of symmetries of a regular %d-gon whose vertices "
            "are labeled 0,1,...,%d in cyclic order; its elements are the rotations and the "
            "reflections of the polygon. In the group, %s. "
            "Let H be the subgroup of D_%d consisting of exactly those symmetries, and consider "
            "the action of H on the vertex set {0,...,%d}. "
            "Report the orbit partition of this action as a list of blocks, each block a sorted "
            "list of vertex labels, and the blocks sorted by their smallest element. For "
            "example, if the orbits are {0}, {1,3} and {2}, write [[0], [1, 3], [2]]."
            % (m, m, m - 1, marked, m, m - 1)
        )

    def score_answer(self, answer, entry):
        gold = _parse_blocks(entry.answer)
        cand = _parse_blocks(answer)
        if gold is None or cand is None:
            return 0.0
        return 1.0 if cand == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'residual_symmetry_under_pinning (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/residual_symmetry_under_pinning',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
