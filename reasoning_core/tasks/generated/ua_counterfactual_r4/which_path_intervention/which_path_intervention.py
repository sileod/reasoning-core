import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


@dataclass
class WhichPathConfig(Config):
    n_nodes: int = 4
    n_blockers: int = 1
    max_weight: int = 2

    def apply_difficulty(self, level):
        self.n_nodes = 4 + level
        self.n_blockers = 1 + level // 3
        self.max_weight = 2 + level


def _gen_graph(rng, n_nodes, max_weight):
    while True:
        order = list(range(n_nodes))
        rng.shuffle(order)
        src, sink = order[0], order[-1]
        edges = []
        for i in range(n_nodes):
            for j in range(i + 1, n_nodes):
                u, v = order[i], order[j]
                if rng.random() < 0.5:
                    w = rng.randint(1, max_weight)
                    edges.append((u, v, w))
        edges = sorted(edges)
        if not edges:
            continue
        src = order[0]
        sink = order[-1]
        yield src, sink, edges


def _all_paths(src, sink, edges):
    adj = {}
    for (u, v, _w) in edges:
        adj.setdefault(u, []).append(v)
    paths = []
    stack = [(src, [src])]
    while stack:
        u, path = stack.pop()
        if u == sink:
            paths.append(list(path))
            continue
        for v in adj.get(u, []):
            if v not in path:
                stack.append((v, path + [v]))
    return paths


def _edge_of(p):
    return [(a, b) for a, b in zip(p, p[1:])]


def _amplitude(p, wmap):
    return Fraction(1, 2 ** sum(wmap[(a, b)] for a, b in _edge_of(p)))


def _parse_fraction(answer):
    a = str(answer).strip()
    if "/" in a:
        try:
            n, d = a.split("/")
            return Fraction(int(n), int(d))
        except (ValueError, ZeroDivisionError):
            return None
    try:
        return Fraction(int(a), 1)
    except (ValueError, ZeroDivisionError):
        return None


class WhichPathIntervention(Task):
    summary = "Alter phase shifts, path blockers and distinguishability tags in finite amplitude networks; combine indistinguishable paths coherently and distinguishable paths incoherently to obtain counterfactual detector probabilities."
    design_choice = "Represent networks as directed acyclic graphs with integer edge weights; answers are reduced fractions for detector probability after specified interventions."
    config_cls = WhichPathConfig

    def generate_entry(self):
        cfg = self.config
        rng = random
        for _ in range(400):
            for src, sink, edges in _gen_graph(rng, cfg.n_nodes, cfg.max_weight):
                paths = _all_paths(src, sink, edges)
                if len(paths) < 2:
                    continue
                wmap = {(u, v): w for (u, v, w) in edges}

                edge_usage = {}
                for p in paths:
                    for (a, b) in _edge_of(p):
                        edge_usage[(a, b)] = edge_usage.get((a, b), 0) + 1

                uniq_candidates = [e for e, c in edge_usage.items() if c == 1]
                if len(uniq_candidates) < 1:
                    continue

                n_blockers = min(cfg.n_blockers, len(uniq_candidates))
                blockers = sorted(rng.sample(uniq_candidates, n_blockers))
                blocked_set = set(blockers)

                remaining = [p for p in paths if not
                             any((a, b) in blocked_set for (a, b) in _edge_of(p))]
                if len(remaining) < 1:
                    continue

                n_dist = rng.randint(0, min(2, len(remaining)))
                dist_indices = set(rng.sample(range(len(remaining)), n_dist))
                distinguishable = [remaining[i] for i in dist_indices]
                coherent = [remaining[i] for i in range(len(remaining)) if i not in dist_indices]

                prob = Fraction(0, 1)
                a_coh = sum((_amplitude(p, wmap) for p in coherent), Fraction(0, 1))
                prob += a_coh * a_coh
                for p in distinguishable:
                    ap = _amplitude(p, wmap)
                    prob += ap * ap

                if not (0 <= prob <= 1):
                    continue
                if prob == 0:
                    continue

                meta = {
                    "n_nodes": cfg.n_nodes,
                    "n_blockers": cfg.n_blockers,
                    "src": src,
                    "sink": sink,
                    "weights": [[u, v, w] for (u, v, w) in edges],
                    "blockers": [[a, b] for (a, b) in blockers],
                    "n_distinguish": n_dist,
                    "relevant_paths": len(remaining),
                    "answer_num": prob.numerator,
                    "answer_den": prob.denominator,
                }
                return Entry(metadata=meta, answer=f"{prob.numerator}/{prob.denominator}")
        raise RuntimeError("could not generate instance")

    def render_prompt(self, metadata):
        edges_str = "; ".join(
            f"{u}->{v} w={w}" for u, v, w in metadata["weights"])
        blockers_str = "; ".join(f"{a}->{b}" for a, b in metadata["blockers"])
        n_dist = metadata["n_distinguish"]
        if n_dist == 0:
            dist_sentence = f"Tag {n_dist} of the remaining indistinguishable paths as distinguishable (so all paths remain one coherent group)."
        else:
            dist_sentence = f"Tag exactly {n_dist} of the remaining indistinguishable paths as distinguishable; the others stay one coherent group."
        return (
            f"A quantum which-path network is a DAG with source {metadata['src']} and sink {metadata['sink']}. "
            f"Edges with integer phase weights: {edges_str}. "
            f"Each path's amplitude is 2^-W where W is the sum of its edge weights. "
            f"Counterfactual intervention: block edge(s) {blockers_str}, removing any path using them. "
            f"{dist_sentence} "
            f"Combine indistinguishable paths coherently (amplitudes add, then square) and distinguishable paths "
            f"incoherently (squared amplitudes add). "
            f"What is the detector probability at the sink after the intervention, as a reduced fraction a/b? "
            f"Answer only the fraction a/b."
        )

    def score_answer(self, answer, entry):
        f = _parse_fraction(answer)
        if f is None:
            return 0.0
        gold = Fraction(entry["metadata"]["answer_num"], entry["metadata"]["answer_den"])
        return 1.0 if f == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'which_path_intervention (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_counterfactual_r4/which_path_intervention',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
