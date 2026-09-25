import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict


TASK_META = {'parent_source_id': None,
 'idea': 'nested_margin_collapse (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_hierarchical_recursive_r4/nested_margin_collapse',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1259343118,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class NestedMarginCollapseConfig(Config):
    min_nodes: int = 3
    max_nodes: int = 6
    depth: int = 2
    min_m: int = -5
    max_m: int = 8
    barrier_p: float = 0.30

    def apply_difficulty(self, level):
        self.min_nodes = 3 + level
        self.max_nodes = 4 + 2 * level
        self.depth = 2 + (level // 2)
        self.min_m = -(4 + level)
        self.max_m = 6 + 2 * level
        self.barrier_p = 0.30


def _collapse(vals):
    """Collapse a set of adjoining vertical margins into one per the CSS rule:
    max positive + min negative (0 for the missing sign)."""
    vals = [v for v in vals]
    if not vals:
        return 0
    pos = [v for v in vals if v >= 0]
    neg = [v for v in vals if v < 0]
    return (max(pos) if pos else 0) + (min(neg) if neg else 0)


def _top_run(node):
    """Margins that adjoin at the very top and collapse together.

    The node's own margin always belongs. It extends down the first-child spine
    while the current (transparent, un-bordered) node has children; a bordered
    node still contributes its own margin but stops the run from descending
    into ITS children.
    """
    run = [node['m']]
    cur = node
    while len(cur['children']) > 0 and not cur['barrier']:
        cur = cur['children'][0]
        run.append(cur['m'])
    return run


def _bottom_run(node):
    run = [node['m']]
    cur = node
    while len(cur['children']) > 0 and not cur['barrier']:
        cur = cur['children'][-1]
        run.append(cur['m'])
    return run


def _build_tree(config):
    n_target = random.randint(config.min_nodes, config.max_nodes)
    counter = [0]

    def new_node(d):
        node = {
            'id': counter[0],
            'm': random.randint(config.min_m, config.max_m),
            'barrier': random.random() < config.barrier_p,
            'children': [],
        }
        counter[0] += 1
        if d > 0 and counter[0] < n_target:
            n_children = 1 if random.random() < 0.55 else 2
            for _ in range(n_children):
                if counter[0] >= n_target:
                    break
                node['children'].append(new_node(d - 1))
        return node

    root = new_node(config.depth)
    return root


def _verify(root, t, b):
    # Recompute from the canonical model and confirm the reported values hold.
    assert _collapse(_top_run(root)) == t
    assert _collapse(_bottom_run(root)) == b
    return True


def _parse_pair(answer):
    try:
        a, bb = [p.strip() for p in str(answer).split(",")]
        return int(a), int(bb)
    except (ValueError, AttributeError):
        return None


class NestedMarginCollapse(Task):
    summary = ("Resolve adjoining vertical margins across nested block boxes, "
               "including negative margins, empty (transparent) descendants, and "
               "border barriers that stop collapse; report the collapsed outer top "
               "and bottom margins as comma-separated integers.")
    config_cls = NestedMarginCollapseConfig
    task_version = 2

    def generate_entry(self):
        for _ in range(2000):
            root = _build_tree(self.config)
            if len(_top_run(root)) < 2 or len(_bottom_run(root)) < 2:
                continue
            t = _collapse(_top_run(root))
            b = _collapse(_bottom_run(root))
            _verify(root, t, b)
            break
        else:
            raise RuntimeError("could not build a non-trivial nested margin tree")

        nodes = []
        order = [root]

        def collect(n):
            nodes.append(n)
            for c in n['children']:
                collect(c)

        collect(root)
        lines = []

        def render(n, indent):
            nlab = "has a border" if n['barrier'] else "no border"
            lines.append(f"{'  ' * indent}Box {n['id']}: margin {n['m']}, {nlab}")
            for c in n['children']:
                render(c, indent + 1)

        render(root, 0)

        metadata = edict({
            'nodes': [{
                'id': int(n['id']),
                'm': int(n['m']),
                'barrier': bool(n['barrier']),
                'children': [int(c['id']) for c in n['children']],
            } for n in nodes],
            't': int(t),
            'b': int(b),
        })
        metadata.payload = {
            'layout': 'Lines are indented to show nesting: each "Box i: margin M, [has a border | no border]" and its direct child boxes follow at one deeper indent.',
            'boxes': '\n'.join(lines),
        }
        return Entry(metadata=metadata, answer=f"{int(t)},{int(b)}")

    def render_prompt(self, metadata):
        body = metadata.payload['boxes']
        head = (
            "The following lines describe vertically nested block boxes, indented "
            "to show nesting. The first box is the outermost; a box's children sit "
            "inside it and are indented one extra level.\n\n"
            f"{body}\n\n"
            "In normal block flow, adjoining vertical margins collapse into a single "
            "margin equal to the maximum positive margin plus the minimum negative "
            "margin (negative-only runs collapse to the most negative value). A box "
            "marked \"no border\" is transparent and empty, so its own margin sits "
            "directly against the margin of its first (for the top run) or last (for "
            "the bottom run) child and collapses through to it. A box marked "
            "\"has a border\" instead stops the collapse right at itself: its own "
            "margin is counted, but the run does not reach that box's children.\n\n"
            "The collapsed outer TOP margin of the entire nested box is the collapse "
            "of the adjoining top run starting at the outermost box's margin and "
            "extending down the first-child spine until a bordered box or a childless "
            "box. The collapsed outer BOTTOM margin is the analogous collapse down "
            "the last-child spine. Apply the collapse rule to the set of margins in "
            "each run.\n\n"
            "Report the collapsed outer TOP margin and the collapsed outer BOTTOM "
            "margin as two comma-separated integers, top first (for example "
            "\"-3,5\"). Answer with only that pair."
        )
        return head

    def score_answer(self, answer, entry):
        parsed = _parse_pair(answer)
        if parsed is None:
            return 0.0
        return 1.0 if parsed == (int(entry.metadata.t), int(entry.metadata.b)) else 0.0
