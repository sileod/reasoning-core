import random
from collections import Counter
from dataclasses import dataclass
from itertools import combinations

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'hypergraph_gyo_reduction (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_reusable_operations_r4/hypergraph_gyo_reduction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def gyo_reduce(edges):
    edges = [(i, list(e)) for i, e in enumerate(edges)]
    steps = []
    while edges:
        cnt = Counter()
        for _, e in edges:
            for v in e:
                cnt[v] += 1
        singles = [v for v in cnt if cnt[v] == 1]
        if singles:
            v = min(singles)
            for k, (oi, e) in enumerate(edges):
                if v in e:
                    e.remove(v)
                    break
            steps.append("v%d" % v)
            edges = [(oi, e) for oi, e in edges if e]
            continue
        done = False
        n = len(edges)
        for i in range(n):
            si = set(edges[i][1])
            for j in range(n):
                if i == j:
                    continue
                if si < set(edges[j][1]):
                    steps.append("e%d" % edges[i][0])
                    edges.pop(i)
                    done = True
                    break
            if done:
                break
        if done:
            continue
        steps.append("BLOCKED")
        return steps
    steps.append("EMPTY")
    return steps


@dataclass
class GyoConfig(Config):
    min_verts: int = 3
    max_verts: int = 4
    min_edges: int = 2
    max_edges: int = 3
    max_span: int = 2

    def apply_difficulty(self, level):
        self.min_verts = 3
        self.max_verts = 4 + level
        self.min_edges = 2
        self.max_edges = 3 + level
        self.max_span = 2 + level


class GyoReduction(Task):
    summary = ("Apply GYO reduction to a hypergraph (delete vertices in one edge, "
               "delete edges contained in another) and give the canonical step "
               "sequence ending in EMPTY or BLOCKED across acyclic and cyclic "
               "input families.")
    config_cls = GyoConfig

    def _gen_interval(self):
        vcount = random.randint(self.config.min_verts, self.config.max_verts)
        m = random.randint(self.config.min_edges, self.config.max_edges)
        edges = []
        for _ in range(m):
            a = random.randint(0, vcount - 2)
            b = random.randint(a + 1, min(a + self.config.max_span, vcount - 1))
            edges.append(list(range(a, b + 1)))
        seen = set()
        uniq = []
        for e in edges:
            t = tuple(e)
            if t not in seen:
                seen.add(t)
                uniq.append(e)
        return uniq

    def _gen_random(self):
        vcount = random.randint(self.config.min_verts, self.config.max_verts)
        m = random.randint(self.config.min_edges, self.config.max_edges)
        edges = []
        for _ in range(m):
            size = random.randint(2, vcount)
            edges.append(sorted(random.sample(range(vcount), size)))
        seen = set()
        uniq = []
        for e in edges:
            t = tuple(e)
            if t not in seen:
                seen.add(t)
                uniq.append(e)
        return uniq

    def _gen_cycle(self):
        k = random.randint(3, min(self.config.max_verts, self.config.max_edges))
        edges = [sorted([i, (i + 1) % k]) for i in range(k)]
        return edges

    def generate_entry(self):
        mode = random.choice(["acyclic", "cyclic"])
        if mode == "acyclic":
            edges = self._gen_interval()
        else:
            edges = None
            for _ in range(30):
                cand = self._gen_random()
                if gyo_reduce(cand)[-1] == "BLOCKED":
                    edges = cand
                    break
            if edges is None:
                edges = self._gen_cycle()
        trace = gyo_reduce(edges)
        verdict = trace[-1]
        assert verdict in ("EMPTY", "BLOCKED")
        assert len(edges) > 0
        return Entry(metadata={
            "edges": [list(e) for e in edges],
            "mode": mode,
            "verdict": verdict,
            "trace": list(trace),
        }, answer=" ".join(trace))

    def render_prompt(self, metadata):
        parts = []
        for i, e in enumerate(metadata["edges"]):
            parts.append("e%d={%s}" % (i, ",".join(map(str, e))))
        edgelist = " ".join(parts)
        return (
            "A hypergraph's vertices are the integers appearing in its edges, listed as "
            "e0,e1,... Reduce it to emptiness with repeated GYO steps:\n"
            "1. If a vertex appears in exactly one edge, delete that vertex from that edge "
            "(step 'v<vertex>').\n"
            "2. Otherwise, if one edge is a proper subset of another edge, delete the "
            "contained edge (step 'e<edge-index>').\n"
            "Repeat until the hypergraph is empty (final word EMPTY) or neither rule applies "
            "(final word BLOCKED).\n"
            "Answer with the steps in order followed by the final word, space-separated. "
            "Format example: for a single edge e0={0,1} the answer is 'v0 v1 EMPTY'.\n"
            "Edges: " + edgelist + "\nAnswer:"
        )

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == entry.answer.strip() else 0.0
