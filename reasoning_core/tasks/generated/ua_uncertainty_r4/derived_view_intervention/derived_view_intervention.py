import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class DerivedViewInterventionV1Config(Config):
    left_count: int = 5
    right_count: int = 4
    extra_edges: int = 3

    def apply_difficulty(self, level):
        self.left_count = 5 + level
        self.right_count = 4 + level
        self.extra_edges = 3 + level


def _join_count(edges, x, y):
    rx = {r for (l, r) in edges if l == x}
    ry = {r for (l, r) in edges if l == y}
    return len(rx & ry)


def _feasible(a, b, left_inds, right_inds, edges):
    """Return 'yes' if a single edge insertion changes only join(a,b) by +1."""
    eset = set(edges)
    left_inds = sorted(left_inds)
    pairs = [(x, y) for i, x in enumerate(left_inds) for y in left_inds[i + 1:]]
    baseline = {(x, y): _join_count(edges, x, y) for (x, y) in pairs}
    target = (min(a, b), max(a, b))
    for r in right_inds:
        for x in left_inds:
            if (x, r) in eset:
                continue
            cand = eset | {(x, r)}
            ok = True
            for (p, q) in pairs:
                delta = _join_count(cand, p, q) - baseline[(p, q)]
                if (p, q) == target:
                    if delta != 1:
                        ok = False
                        break
                else:
                    if delta != 0:
                        ok = False
                        break
            if ok:
                return 'yes'
    return 'no'


def _build_edges(case, a, b, left_inds, right_inds, extra_edges):
    L = sorted(left_inds)
    R = sorted(right_inds)
    edges = set()
    if case == 'yes':
        lonely = R[0]
        edges.add((b, lonely))
        for r in R[1:]:
            pair = random.sample([x for x in L], 2)
            edges.add((pair[0], r))
            edges.add((pair[1], r))
        eligible = [r for r in R[1:] if r != lonely]
    else:
        for r in R:
            pair = random.sample([x for x in L], 2)
            edges.add((pair[0], r))
            edges.add((pair[1], r))
        eligible = R
    added = 0
    attempts = 0
    while added < extra_edges and attempts < 100:
        attempts += 1
        r = random.choice(eligible)
        x = random.choice(L)
        if (x, r) in edges:
            continue
        edges.add((x, r))
        added += 1
    return edges


class DerivedViewIntervention(Task):
    summary = ("Impose counterfactual changes on derived join-view counts of a bipartite "
               "graph of base facts; decide whether the fewest single edge edit raises one "
               "pair's shared-neighbor count without collateral change to any other join, "
               "or is impossible because every candidate right entity also joins elsewhere.")
    config_cls = DerivedViewInterventionV1Config

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.balancing_key_ratio = 1.0

    design_choice = ("Represent base facts as a bipartite graph and ask for edge insertions/"
                     "deletions that alter only the derived join-view counts, with impossibility "
                     "when cycles force collateral changes.")

    def generate_entry(self):
        cfg = self.config
        L = list(range(cfg.left_count))
        R = list(range(cfg.right_count))
        a, b = random.sample(L, 2)
        case = random.choice(['yes', 'no'])
        edges = None
        for _ in range(200):
            edges = _build_edges(case, a, b, L, R, cfg.extra_edges)
            if _feasible(a, b, L, R, edges) == case:
                break
        else:
            raise RuntimeError("failed to build a consistent intervention graph")

        answer = _feasible(a, b, L, R, edges)
        edge_list = sorted((l, r) for (l, r) in edges)
        metadata = {
            "left": [f"L{i}" for i in L],
            "right": [f"R{i}" for i in R],
            "a": f"L{a}",
            "b": f"L{b}",
            "edges": [[l, r] for (l, r) in edge_list],
            "answer_yes": (answer == 'yes'),
        }
        return Entry(metadata=metadata, answer="Yes" if answer == 'yes' else "No")

    def render_prompt(self, metadata):
        left = ", ".join(metadata["left"])
        right = ", ".join(metadata["right"])
        edges = "".join("  (%s, %s)\n" % ("L%d" % l, "R%d" % r) for (l, r) in metadata["edges"])
        a = metadata["a"]
        b = metadata["b"]
        return (
            "We have left entities {%s} and right entities {%s}. "
            "The currently true base facts (edges) are:\n%s"
            "For every pair of distinct left entities (x, y), the derived join-view "
            "join(x,y) is the number of right entities adjacent to both x and y. Reply "
            "exactly Yes or No.\n"
            "Goal: insert and/or delete base-fact edges so that join(%s, %s) increases by "
            "exactly 1, while every other join-view stays exactly as it is now, using the "
            "fewest such edge edits. You may add or remove edges only between the listed "
            "left and right entities; you may not add new left or right entities.\n"
            "Is such an intervention achievable?" % (left, right, edges, a, b)
        )

    def score_answer(self, answer, entry):
        ref = str(entry["answer"]).strip().lower()
        ans = str(answer).strip().lower()
        return 1.0 if ans == ref else 0.0

    def distractor_candidates(self, entry):
        return ["No" if entry["answer"] == "Yes" else "Yes"]


TASK_META = {'parent_source_id': None,
 'idea': 'derived_view_intervention (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_uncertainty_r4/derived_view_intervention',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
