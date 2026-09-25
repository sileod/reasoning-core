import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class AntichainConfig(Config):
    nodes: int = 5
    edges: int = 4
    frontiers: int = 2

    def apply_difficulty(self, level):
        self.nodes = 4 + level
        self.edges = 3 + level
        self.frontiers = 1 + level // 3


class AntichainProgress(Task):
    summary = "Track progress frontiers in partially ordered timestamp spaces through advances, forks, and joins; determine which queried times are complete because no frontier element can still precede them."
    design_choice = "Represent each partial order as a DAG of integer timestamps with edges denoting precedence; queries ask whether a target timestamp is dominated by any frontier element, with answers as boolean strings."

    config_cls = AntichainConfig
    task_version = 2

    def generate_entry(self):
        nodes = self.config.nodes
        edges = self.config.edges
        nfront = self.config.frontiers

        while True:
            times = random.sample(range(0, 100), nodes)
            edgeset = set()
            attempts = 0
            while len(edgeset) < edges and attempts < 200:
                attempts += 1
                u, v = random.sample(range(nodes), 2)
                if u == v:
                    continue
                if (u, v) in edgeset or (v, u) in edgeset:
                    continue
                # reject creating a cycle: v must not reach u
                if _reaches(v, u, edgeset, nodes):
                    continue
                edgeset.add((u, v))
            if len(edgeset) < edges:
                continue

            # progress frontiers: subsets of nodes
            frontiers = set()
            curr = 0
            while curr < nfront * 20:
                if len(frontiers) == nfront:
                    break
                k = random.randint(1, nodes)
                candidate = tuple(sorted(random.sample(range(nodes), k)))
                if candidate not in frontiers:
                    frontiers.add(candidate)
                curr += 1
            if len(frontiers) != nfront:
                continue

            # feel for whether a frontier element can reach a given node
            def dominated(q):
                return any(_reaches(f, q, edgeset, nodes) for fr in frontiers for f in fr)

            # choose at least 2 queries with both labels present
            nq = max(nfront, 2)
            queries = []
            for _ in range(nq):
                queries.append(random.randint(0, nodes - 1))
            values = set(dominated(q) for q in queries)
            guard = 0
            while len(values) < 2 and guard < 100:
                guard += 1
                queries = [random.randint(0, nodes - 1) for _ in range(nq)]
                values = set(dominated(q) for q in queries)
            if len(values) < 2:
                continue
            answers = [dominated(q) for q in queries]

            # metadata
            meta = {
                "nodes": nodes,
                "edges": list(edgeset),
                "times": times,
                "frontiers": [list(f) for f in sorted(frontiers)],
                "queries": queries,
            }
            answer = " ".join("Yes" if a else "No" for a in answers)
            return Entry(metadata=meta, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append("A distributed system advances through events carrying integer timestamps. Some timestamps are known to precede others, giving a partial order:")
        for u, v in sorted(metadata["edges"]):
            lines.append(f"- timestamp {metadata['times'][u]} precedes timestamp {metadata['times'][v]}")
        lines.append("Precedence is transitive: if a precedes b and b precedes c, then a precedes c.")
        lines.append("")
        lines.append("A progress frontier is a set of reached timestamps. Treat each frontier as the whole set of reached events so far. A queried timestamp is DOMINATED if some frontier timestamp precedes it (directly or transitively) or equals it; otherwise it is NOT dominated.")
        for i, fr in enumerate(metadata["frontiers"]):
            ts = sorted(metadata["times"][x] for x in fr)
            lines.append(f"Frontier {i + 1} contains timestamps: {ts}")
        lines.append("")
        lines.append("For each queried timestamp, answer Yes if it is dominated by a frontier element, otherwise No.")
        for q in metadata["queries"]:
            lines.append(f"- Is timestamp {metadata['times'][q]} dominated?")
        lines.append("")
        lines.append("Reply with Yes or No for each query, in order, separated by spaces.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        expected = entry.answer
        if answer.strip() == expected:
            return 1.0
        toks = [t for t in answer.strip().split()]
        etoks = expected.split()
        if toks == etoks:
            return 1.0
        return 0.0


def _reaches(source, target, edgeset, nodes):
    stack = [source]
    seen = {source}
    while stack:
        x = stack.pop()
        if x == target:
            return True
        for (u, v) in edgeset:
            if u == x and v not in seen:
                seen.add(v)
                stack.append(v)
    return False


TASK_META = {'parent_source_id': None,
 'idea': 'antichain_progress_completion (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/antichain_progress_completion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
