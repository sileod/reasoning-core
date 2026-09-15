import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'ordered_greedy_coloring (draw 2 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/ordered_greedy_coloring',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 525660630,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _color_order(adjacency, order):
    color = {}
    for v in order:
        used = {color[u] for u in adjacency[v] if u in color}
        c = 1
        while c in used:
            c += 1
        color[v] = c
    return color


def _graph_family(family, n):
    adjacency = {i: set() for i in range(n)}
    if family == 'path':
        for i in range(n - 1):
            adjacency[i].add(i + 1)
            adjacency[i + 1].add(i)
    elif family == 'cycle':
        for i in range(n):
            adjacency[i].add((i + 1) % n)
            adjacency[(i + 1) % n].add(i)
    elif family == 'tree':
        for i in range(1, n):
            p = random.randrange(i)
            adjacency[i].add(p)
            adjacency[p].add(i)
    elif family == 'grid':
        cols = random.randrange(2, min(n, 5))
        rows = (n + cols - 1) // cols
        idx = {}
        counter = 0
        for r in range(rows):
            for c in range(cols):
                if counter < n:
                    idx[(r, c)] = counter
                    counter += 1

        def add(a, b):
            adjacency[a].add(b)
            adjacency[b].add(a)

        for (r, c), v in idx.items():
            if (r + 1, c) in idx:
                add(v, idx[(r + 1, c)])
            if (r, c + 1) in idx:
                add(v, idx[(r, c + 1)])
    return adjacency


@dataclass
class ColoringConfig(Config):
    family: str = 'path'
    n: int = 4
    output: str = 'color'
    query: int = 0

    def apply_difficulty(self, level):
        self.n = stochastic_rounding(6 + 2 * level)
        families = ['path', 'path', 'cycle', 'tree', 'grid']
        self.family = families[min(level, 4)]
        self.output = None


class OrderedGreedyColoring(Task):
    summary = ("Assign each vertex the smallest color unused by earlier-colored "
               "neighbors under a stated processing order, returning a queried "
               "vertex's color, the number of colors used, or the full assignment "
               "across varied graph shapes (paths, cycles, trees, grids).")
    design_choice = ("Vary the queried output: sometimes ask for a single vertex's "
                     "color, sometimes the total color count, sometimes the full "
                     "assignment, with instances generated from different graph "
                     "families (paths, cycles, trees, grids).")
    config_cls = ColoringConfig

    def generate_entry(self):
        cfg = self.config
        n = max(2, int(round(cfg.n)))
        adjacency = _graph_family(cfg.family, n)
        order = list(range(n))
        random.shuffle(order)
        color = _color_order(adjacency, order)
        num_used = len(set(color.values()))
        if cfg.family == 'grid':
            output = random.choice(['color', 'count', 'assignment'])
        elif cfg.family == 'tree':
            output = random.choice(['color', 'assignment'])
        else:
            output = 'color'
        query = None
        if output == 'color':
            query = order[-1]
            answer = str(color[query])
        elif output == 'count':
            answer = str(num_used)
        else:
            assignment = [color[v] for v in range(n)]
            answer = ' '.join(str(c) for c in assignment)
        adj_str = {str(v): sorted(u for u in adjacency[v]) for v in adjacency}
        metadata = {
            'family': cfg.family,
            'order': list(order),
            'adjacency': adj_str,
            'output': output,
            'query': query,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        n = len(metadata['order'])
        parts = []
        for i in range(n):
            nb = ','.join(f'v{j}' for j in metadata['adjacency'][str(i)])
            parts.append(f'v{i}:{{{nb}}}')
        verts = ' '.join(parts)
        order = ' -> '.join(f'v{i}' for i in metadata['order'])
        lines = [
            f"A graph has vertices v0..v{n - 1} with edges: {verts}.",
            f"The greedy coloring processes them in order {order}.",
            "Each vertex receives the smallest color 1,2,3,... not yet used by "
            "any of its already-colored neighbors.",
        ]
        out = metadata['output']
        if out == 'color':
            lines.append(f"What color does v{metadata['query']} receive? Answer with one integer.")
        elif out == 'count':
            lines.append("How many distinct colors are used in total? Answer with one integer.")
        else:
            lines.append("List the full assignment as v0,v1,... colors separated by spaces.")
        return '\n'.join(lines)

    def score_answer(self, answer, entry):
        out = entry.metadata['output']
        gold = entry.answer
        if out in ('color', 'count'):
            try:
                return 1.0 if int(str(answer).strip()) == int(gold) else 0.0
            except (ValueError, TypeError):
                return 0.0
        try:
            got = [int(x) for x in str(answer).split()]
            exp = [int(x) for x in gold.split()]
            if len(got) != len(exp):
                return 0.0
            return 1.0 if got == exp else 0.0
        except (ValueError, TypeError):
            return 0.0
