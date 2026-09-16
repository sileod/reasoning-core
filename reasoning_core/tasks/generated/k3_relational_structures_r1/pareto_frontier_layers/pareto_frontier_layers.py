import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class ParetoLayersConfig(Config):
    n_points: int = 6
    k_dim: int = 2
    n_front: int = 2
    mode: str = "layers"

    def apply_difficulty(self, level):
        self.n_points = stochastic_rounding(6 + 2 * level)
        self.k_dim = 2 if level < 3 else (3 if level < 5 else 4)
        self.n_front = stochastic_rounding(1 + level // 2)


def _dominates(a, b, maximize):
    if maximize:
        return all(x >= y for x, y in zip(a, b)) and any(x > y for x, y in zip(a, b))
    return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))


def _pareto_layers(points, maximize):
    remaining = list(range(len(points)))
    layer_of = [None] * len(points)
    layer = 1
    while remaining:
        front = [
            i
            for i in remaining
            if not any(_dominates(points[j], points[i], maximize) for j in remaining)
        ]
        for i in front:
            layer_of[i] = layer
        remaining = [i for i in remaining if i not in front]
        layer += 1
    return layer_of


def _sorted_pareto_fronts(points, maximize):
    remaining = list(range(len(points)))
    fronts = []
    while remaining:
        front = [
            i
            for i in remaining
            if not any(_dominates(points[j], points[i], maximize) for j in remaining)
        ]
        front.sort()
        fronts.append(front)
        remaining = [i for i in remaining if i not in front]
    return fronts


def _dom_counts(points, maximize):
    return [
        sum(1 for j in range(len(points)) if i != j and _dominates(points[j], points[i], maximize))
        for i in range(len(points))
    ]


def _pair_labels(points, maximize, edges):
    labels = []
    for (i, j) in edges:
        pi, pj = points[i], points[j]
        if pi == pj:
            labels.append("E")
        elif all((x <= y) if not mx else (x >= y) for x, y, mx in zip(pi, pj, maximize)):
            labels.append("D")
        else:
            labels.append("N")
    return labels


TASK_META = {'parent_source_id': None,
 'idea': 'pareto_frontier_layers (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/pareto_frontier_layers',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class ParetoFrontierLayers(Task):
    summary = "Strip iterated Pareto fronts from point sets under coordinatewise or mixed min/max dominance; modes return each point's layer, the k-th frontier as sorted indices, per-point domination counts, or verdicts on queried pairs."
    config_cls = ParetoLayersConfig
    design_choice = "Answer form: per-point layer labels as a compact string of integers, e.g., '1 2 1 3', with layers numbered from 1 outward."

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_points
        k = cfg.k_dim
        mode = random.choice(["layers", "kfront", "counts", "pairs"])

        maximize = [random.choice([True, False]) for _ in range(k)]
        while True:
            points = []
            for _ in range(n):
                points.append([random.randint(0, 9) for _ in range(k)])
            if len({tuple(p) for p in points}) >= 2:
                break

        if mode == "layers":
            layer_of = _pareto_layers(points, maximize)
            fronts = _sorted_pareto_fronts(points, maximize)
            rebuilt = [None] * n
            for li, front in enumerate(fronts, start=1):
                for i in front:
                    rebuilt[i] = li
            assert rebuilt == layer_of, "layer reconstruction failed"
            answer = " ".join(str(l) for l in layer_of)
            metadata = {"points": points, "mode": mode, "maximize": maximize}
            return Entry(metadata=metadata, answer=answer)

        if mode == "kfront":
            fronts = _sorted_pareto_fronts(points, maximize)
            if len(fronts) < 2:
                return self.generate_entry()
            ksel = random.randrange(1, min(cfg.n_front, len(fronts)) + 1)
            front_indices = fronts[ksel - 1]
            layer_of = _pareto_layers(points, maximize)
            assert all(layer_of[i] == ksel for i in front_indices), "kfront layer mismatch"
            for i in range(n):
                if i not in front_indices:
                    assert layer_of[i] != ksel, "kfront missing a layer member"
            answer = " ".join(str(i) for i in front_indices)
            metadata = {"points": points, "mode": mode, "maximize": maximize, "k": int(ksel)}
            return Entry(metadata=metadata, answer=answer)

        if mode == "counts":
            counts = _dom_counts(points, maximize)
            for i in range(n):
                dom = sum(1 for j in range(n) if j != i and _dominates(points[j], points[i], maximize))
                assert dom == counts[i], "count mismatch"
            assert all(0 <= c <= n - 1 for c in counts), "count out of domain"
            answer = " ".join(str(c) for c in counts)
            metadata = {"points": points, "mode": mode, "maximize": maximize}
            return Entry(metadata=metadata, answer=answer)

        flat = [(i, j) for i in range(n) for j in range(n)]
        nq = random.randint(2, min(4, len(flat)))
        edges = []
        for _ in range(nq):
            edges.append(random.choice(flat))
        labels = _pair_labels(points, maximize, edges)
        assert _pair_labels(points, maximize, edges) == labels, "pairs label mismatch"
        for lbl in labels:
            assert lbl in ("D", "E", "N"), "pairs label out of domain"
        answer = " ".join(labels)
        metadata = {"points": points, "mode": mode, "maximize": maximize,
                    "pairs": [[int(i), int(j)] for (i, j) in edges]}
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        mode = metadata["mode"]
        pts = " ".join(
            "(" + ",".join(str(v) for v in p) + ")" for p in metadata["points"]
        )
        directions = " ".join("max" if mx else "min" for mx in metadata["maximize"])
        head = (
            f"Points (index 0 first): {pts}. Coordinate directions, in order: {directions}, "
            f"where 'max' means larger is better and 'min' means smaller is better. "
            f"Under Pareto dominance, a point dominates another when it is at least as good "
            f"in every coordinate and strictly better in at least one."
        )

        if mode == "layers":
            return (
                head + " Strip the iterated Pareto fronts: the set of points not dominated by "
                "anything else is the first (outermost) front, layer 1; removing it reveals "
                "layer 2, and so on. Give, for each point in index order, its layer number, "
                "space-separated (e.g., '1 2 1 3')."
            )
        if mode == "kfront":
            ksel = metadata["k"]
            return (
                head + f" Strip the iterated Pareto fronts, numbered outwards from 1. Report "
                f"the indices of the points in layer {ksel}, in increasing index order, "
                f"space-separated."
            )
        if mode == "counts":
            return (
                head + " For each point in index order, report how many OTHER points dominate "
                "it, space-separated."
            )
        pstr = "; ".join(f"query ({i},{j})" for (i, j) in metadata["pairs"])
        return (
            head + " For each queried pair (i,j), write 'D' if point i dominates or is strictly "
            "better than point j, 'E' if the two points are equal, otherwise 'N'. "
            f"Queries: {pstr}. Give one symbol per query in order, space-separated."
        )

    def score_answer(self, answer, entry):
        mode = entry.metadata["mode"]
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        if mode == "pairs":
            a = answer.split()
            g = gold.split()
            return 1.0 if (a == g and len(a) == len(g)) else 0.0
        return 1.0 if answer.strip() == gold else 0.0
