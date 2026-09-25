"""Guillotine layout extent v2.

Determine enclosing dimensions for recursively sliced layouts with rotatable leaf
rectangles, cut gutters, and alignment constraints. Leaf rectangles may be rotated
90 degrees; cut gutters subtract a fixed width from each gutter cut; alignment
constraints require leaf edges to align with cut lines across sibling subtrees,
so solvers grow the smaller child to satisfy shared boundaries.

The answer is the minimum-area feasible WxH over all rotation choices.
Tree is stored in metadata as a JSON-serializable nested structure.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class GuillotineLayoutExtentV2Config(Config):
    leaves: int = 4
    max_size: int = 25
    gutter: int = 2
    gutter_prob: float = 0.5

    def apply_difficulty(self, level):
        self.leaves = 2 + level + (level >= 3)
        self.max_size = 15 + 5 * level
        self.gutter = 1 + (level >= 4)
        self.gutter_prob = 0.3 + 0.1 * level


def _rot(dim, rot):
    return (dim[1], dim[0]) if rot else dim


def _make_tree(items):
    if len(items) == 1:
        return ("L", items[0])
    k = random.randint(1, len(items) - 1)
    left = _make_tree(items[:k])
    right = _make_tree(items[k:])
    ctype = random.choice(["V", "H"])
    return (ctype, left, right)


def _mark_gutters(node, prob, flags):
    if node[0] == "L":
        return
    if random.random() < prob:
        flags[id(node)] = True
    _mark_gutters(node[1], prob, flags)
    _mark_gutters(node[2], prob, flags)


def _extent(node, oriented, gutter, flags):
    if node[0] == "L":
        return oriented[node[1]]
    ctype, l, r = node
    lw, lh = _extent(l, oriented, gutter, flags)
    rw, rh = _extent(r, oriented, gutter, flags)
    is_g = id(node) in flags
    if ctype == "V":
        return (lw + rw + (gutter if is_g else 0), max(lh, rh))
    return (max(lw, rw), lh + rh + (gutter if is_g else 0))


def _serialize(node, flags):
    if node[0] == "L":
        return ["L", node[1]]
    ctype, l, r = node
    tag = ("Vg" if ctype == "V" else "Hg") if id(node) in flags else ctype
    return [tag, _serialize(l, flags), _serialize(r, flags)]


class GuillotineLayoutExtent(Task):
    summary = "Determine enclosing dimensions for recursively sliced layouts with rotatable leaf rectangles, cut gutters, and alignment constraints; vary horizontal and vertical nesting; answer the minimum-area feasible dimensions."
    design_choice = "Alignment constraints require leaf edges to align with cut lines across sibling subtrees, so solvers must adjust dimensions to satisfy shared boundaries."
    config_cls = GuillotineLayoutExtentV2Config

    def generate_entry(self):
        cfg = self.config
        n_leaves = cfg.leaves
        max_size = cfg.max_size
        gutter = cfg.gutter

        leaves = [(random.randint(1, max_size), random.randint(1, max_size))
                  for _ in range(n_leaves)]
        tree = _make_tree(list(range(n_leaves)))

        flags = {}
        _mark_gutters(tree, cfg.gutter_prob, flags)

        best = None
        for mask in range(1 << n_leaves):
            oriented = [_rot(leaves[i], (mask >> i) & 1) for i in range(n_leaves)]
            w, h = _extent(tree, oriented, gutter, flags)
            area = w * h
            if best is None or area < best[0] or (area == best[0] and (w, h) < (best[1], best[2])):
                best = (area, w, h)

        area, answer_w, answer_h = best
        assert answer_w >= 1 and answer_h >= 1
        assert isinstance(answer_w, int) and isinstance(answer_h, int)

        tree_json = _serialize(tree, flags)
        metadata = {
            "leaves": leaves,
            "gutter": gutter,
            "tree": tree_json,
            "answer_w": answer_w,
            "answer_h": answer_h,
        }
        return Entry(metadata=metadata, answer=f"{answer_w}x{answer_h}")

    def render_prompt(self, metadata):
        leaves = metadata["leaves"]
        gutter = metadata["gutter"]

        def render(node):
            if node[0] == "L":
                return str(node[1])
            return f"{node[0]}({render(node[1])},{render(node[2])})"

        lines = []
        lines.append("A guillotine layout packs leaf rectangles that may each be rotated 90")
        lines.append("degrees (equivalently swapping width and height). The slicing plan is a")
        lines.append("binary tree. Each internal cut is V (vertical: sub-blocks sit side by")
        lines.append("side, widths add, and heights are forced to align across the shared cut)")
        lines.append("or H (horizontal: sub-blocks stack, heights add, widths align). A cut")
        lines.append("marked Vg or Hg is a gutter cut running on the same V or H axis but")
        lines.append("additionally consuming a fixed gutter width from the spliced span.")
        lines.append("")
        lines.append("Leaf rectangles (width x height):")
        for i, (w, h) in enumerate(leaves):
            lines.append(f"  leaf {i}: {w}x{h}")
        lines.append(f"Gutter width: {gutter}")
        lines.append("")
        lines.append("Slicing plan (root left; leaf indices; L means leaf):")
        lines.append("  " + render(metadata["tree"]))
        lines.append("")
        lines.append("Rotations are chosen to minimize enclosing area. Because leaf edges must")
        lines.append("align with cut lines across sibling subtrees, the smaller sibling is")
        lines.append("grown to the larger in the shared dimension. Report the minimum-area")
        lines.append("enclosing width and height as WxH (e.g. 14x9).")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            return 1.0 if str(answer).strip() == entry.answer else 0.0
        except Exception:
            return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'guillotine_layout_extent (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/guillotine_layout_extent',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
