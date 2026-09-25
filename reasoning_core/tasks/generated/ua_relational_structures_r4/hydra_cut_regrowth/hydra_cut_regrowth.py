import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class HydraConfig(Config):
    max_depth: int = 3
    branch: int = 3
    num_cuts: int = 1

    def apply_difficulty(self, level):
        self.max_depth = 3 + (level // 2)
        self.branch = 3 + (level // 2)
        self.num_cuts = 1 + (level // 2)


MAX_HEADS = 100000


def _copy(node):
    return [_copy(c) for c in node]


def _render(node):
    if len(node) == 0:
        return "h"
    return "(" + " ".join(_render(c) for c in node) + ")"


def _find_leaf(root, depth):
    def rec(node, nd, gp, p):
        if nd == depth and len(node) == 0:
            return (gp, p, node)
        for c in node:
            r = rec(c, nd + 1, p, node)
            if r is not None:
                return r
        return None

    return rec(root, 0, None, None)


def _available_depths(root):
    depths = set()

    def rec(node, nd):
        if len(node) == 0 and nd >= 1:
            depths.add(nd)
        for c in node:
            rec(c, nd + 1)

    rec(root, 0)
    return sorted(depths)


def _count_heads(node, is_root):
    if len(node) == 0:
        return 0 if is_root else 1
    return sum(_count_heads(c, False) for c in node)


def _cut(root, depth):
    found = _find_leaf(root, depth)
    if found is None:
        return False
    grandparent, parent, leaf = found
    parent.remove(leaf)
    if grandparent is None:
        return True
    siblings = [s for s in grandparent if s is not parent]
    for _ in range(depth):
        for s in siblings:
            grandparent.append(_copy(s))
    return True


def _build(depth_target, branch):
    if depth_target <= 0:
        return []
    k = random.randint(1, branch)
    children = []
    first = depth_target - 1
    for i in range(k):
        cd = first if i == 0 else random.randint(0, depth_target - 1)
        children.append(_build(cd, branch))
    return children


def _apply_cuts(root, depths):
    cur = root
    for d in depths:
        if not _cut(cur, d):
            return None
    return cur


TASK_META = {'parent_source_id': None,
 'idea': 'hydra_cut_regrowth (variant 2 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/hydra_cut_regrowth',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 382564971,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class HydraCutRegrowth(Task):
    summary = "Apply leaf-cut and ancestor-copy rules to hydra trees, varying cut depth, sibling order, move-dependent regrowth, and successive cuts; determine the remaining head count."
    design_choice = "Return only the final number of heads as an integer, using a fixed global rule that each cut at depth d regrows d copies of the parent's siblings."
    config_cls = HydraConfig

    def generate_entry(self):
        for _ in range(2000):
            root = _build(self.config.max_depth, self.config.branch)
            depths = []
            cur = _copy(root)
            for _ in range(self.config.num_cuts):
                avail = _available_depths(cur)
                if not avail:
                    break
                d = random.choice(avail)
                cur = _apply_cuts(cur, [d])
                if cur is None:
                    break
                depths.append(d)
            if len(depths) < self.config.num_cuts:
                continue
            heads = _count_heads(cur, True)
            if heads < 1 or heads > MAX_HEADS:
                continue
            depth_seq = [int(d) for d in depths]
            metadata = {
                "initial_str": _render(root),
                "depth_seq": depth_seq,
                "max_depth": int(self.config.max_depth),
                "branch": int(self.config.branch),
                "num_cuts": int(self.config.num_cuts),
            }
            return Entry(metadata=metadata, answer=str(int(heads)))
        raise RuntimeError("hydra generation failed to converge")

    def render_prompt(self, metadata):
        depth_seq = ", ".join(str(d) for d in metadata["depth_seq"])
        return (
            "A hydra is a rooted tree of heads. It is written with nested parentheses: "
            "each ( ... ) is a body node and each h is a head (a leaf). Siblings are "
            "ordered left to right. The root is the outermost ( ... ) group, at depth 0; "
            "a head at depth d has d edges to the root.\n"
            "Hydra rule: to cut a head at depth d, remove that h. If the head's parent is "
            "not the root, the parent then regrows d fresh copies of each of its own "
            "siblings (the other children of its parent); these copies are attached under "
            "the head's grandparent. If the head's parent is the root, nothing regrows.\n"
            f"Starting hydra: {metadata['initial_str']}\n"
            "Perform cuts in the stated order, each time cutting the leftmost head "
            "(scanning left to right) located at the given depth in the tree as it "
            f"currently stands, at depths: {depth_seq}.\n"
            "After all cuts, how many heads (h tokens) remain? "
            "Answer with the integer head count."
        )

    def score_answer(self, answer, entry):
        try:
            val = int(str(answer).strip())
        except (ValueError, TypeError):
            return 0.0
        return 1.0 if val == int(entry.answer) else 0.0
