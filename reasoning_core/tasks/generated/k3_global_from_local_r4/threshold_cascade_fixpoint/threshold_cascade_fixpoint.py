import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'threshold_cascade_fixpoint (variant 2 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_global_from_local_r4/threshold_cascade_fixpoint',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3020341981,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class ThresholdCascadeConfig(Config):
    nodes: int = 5
    max_threshold: int = 3

    def apply_difficulty(self, level):
        self.nodes = stochastic_rounding(5 + level * 1.5, seed=random.randrange(2**32))
        self.max_threshold = stochastic_rounding(2 + level * 0.7, seed=random.randrange(2**32))


def _run_cascade(neighbors, thresholds, seed_nodes):
    active = set(seed_nodes)
    turn_on = {0}
    rounds = {}
    for n in seed_nodes:
        rounds[n] = 1
    t = 1
    while turn_on:
        t += 1
        nxt = set()
        for v in neighbors:
            if v in active:
                continue
            cnt = sum(1 for u in neighbors[v] if u in active)
            if cnt >= thresholds[v]:
                nxt.add(v)
        for v in nxt:
            if v not in rounds:
                rounds[v] = t
        active |= nxt
        turn_on = nxt
    return active, rounds


class ThresholdCascadeFixpoint(Task):
    summary = "Digraphs with per-node activation thresholds and a seed set: a node turns active once enough in-neighbors are active, applied in rounds; answer the final active set in ascending order, the round a queried node turns on, or whether the process saturates (all nodes active)."
    design_choice = "Answer format is a canonical comma-separated list of node labels in ascending order for the final active set, with ties broken by round number for queried nodes."
    config_cls = ThresholdCascadeConfig

    def _render_common(self, metadata):
        lines = []
        n = metadata['nodes']
        lines.append("A directed graph has nodes 0..%d. A directed edge u->v makes u an in-neighbor of v." % (n - 1))
        edges_list = []
        for v, ns in metadata['neighbors'].items():
            for u in ns:
                edges_list.append("%d->%d" % (int(u), int(v)))
        if edges_list:
            lines.append("Edges: " + ", ".join(sorted(edges_list)))
        lines.append("Each node v activates once the number of its already-active in-neighbors reaches its threshold t(v).")
        th = ", ".join("t(%d)=%d" % (i, metadata['thresholds'][i]) for i in range(n))
        lines.append("Thresholds: " + th)
        lines.append("Initially active (round 1): " + ", ".join(str(x) for x in metadata['seeds']))
        lines.append("Activation proceeds in rounds: in each round, every not-yet-active node with enough currently-active in-neighbors becomes active; repeat until stable.")
        return lines

    def _random_entry(self, cfg):
        while True:
            n = cfg.nodes
            nodes = list(range(n))
            edges = set()
            for u in nodes:
                out = random.sample([v for v in nodes if v != u],
                                    random.randint(1, max(1, min(3, n - 1))))
                for v in out:
                    edges.add((u, v))
            neighbors = {v: [] for v in nodes}
            for u, v in edges:
                neighbors[v].append(u)
            thresholds = [random.randint(1, cfg.max_threshold) for _ in nodes]
            seed_count = random.randint(1, max(1, n // 3))
            seed_nodes = set(random.sample(nodes, seed_count))
            active, rounds = _run_cascade(neighbors, thresholds, seed_nodes)
            if not active:
                continue
            mode = random.choice(['set', 'round'])
            metadata = {
                'nodes': n,
                'neighbors': {str(v): sorted(ns) for v, ns in neighbors.items()},
                'thresholds': thresholds,
                'seeds': sorted(seed_nodes),
                'mode': mode,
            }
            if mode == 'set':
                answer = ','.join(str(x) for x in sorted(active))
            else:
                turnable = [v for v in nodes if v in rounds and v not in seed_nodes]
                if not turnable:
                    continue
                target = random.choice(turnable)
                metadata['query'] = target
                answer = str(rounds[target])
            return Entry(metadata=metadata, answer=answer)

    def _saturate_entry(self, cfg):
        n = cfg.nodes
        order = list(range(n))
        random.shuffle(order)
        seed_nodes = set(order[:1])
        neighbors = {v: [] for v in range(n)}
        for k in range(1, n):
            earlier = order[:k]
            neighbors[order[k]] = list(earlier)
        target = random.random() < 0.5
        thresholds = [1] * n
        if not target:
            thresholds[order[n - 1]] = n
        active, _ = _run_cascade(neighbors, thresholds, seed_nodes)
        sat = len(active) == n
        if target:
            assert sat, "expected saturation"
        else:
            assert sat is False, "expected non-saturation"
        metadata = {
            'nodes': n,
            'neighbors': {str(v): sorted(ns) for v, ns in neighbors.items()},
            'thresholds': thresholds,
            'seeds': sorted(seed_nodes),
            'mode': 'saturate',
            'saturates': sat,
        }
        answer = 'yes' if sat else 'no'
        return Entry(metadata=metadata, answer=answer)

    def generate_entry(self):
        cfg = self.config
        mode = random.choice(['set', 'round', 'saturate'])
        if mode == 'saturate':
            return self._saturate_entry(cfg)
        return self._random_entry(cfg)

    def render_prompt(self, metadata):
        lines = self._render_common(metadata)
        mode = metadata['mode']
        if mode == 'set':
            lines.append("Answer with the final active set as a comma-separated list of node labels in ascending order, nothing else.")
        elif mode == 'round':
            lines.append("In which round does node %d first become active? Answer with a single integer only." % metadata['query'])
        else:
            lines.append("Does the process saturate and activate every node? Reply with the single word yes or no and no extra text.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        expected = entry.answer
        if not isinstance(answer, str):
            return 0.0
        ans = answer.strip()
        mode = entry.metadata['mode']
        if mode == 'round' or mode == 'saturate':
            return 1.0 if ans == expected else 0.0
        try:
            got = [int(x.strip()) for x in ans.replace(',', ' ').split() if x.strip() != '']
        except ValueError:
            return 0.0
        exp = [int(x) for x in expected.split(',')]
        return 1.0 if sorted(got) == sorted(exp) else 0.0
