import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


ATTRS = ["A", "B", "C", "D", "E", "F", "G"]


def _pick_split(rows):
    attrs = [k for k in rows[0] if k != "label"]
    attr_exhausted = 0
    best_attr, best_gain, best_split = None, None, None
    for attr in attrs:
        values = {r[attr] for r in rows}
        if len(values) < 2:
            attr_exhausted += 1
            continue
        gain, split = _max_gain_for_attr(rows, attr)
        if best_attr is None or gain > best_gain or (gain == best_gain and attr < best_attr):
            best_gain, best_attr, best_split = gain, attr, split
    return best_attr, best_gain, best_split, attr_exhausted


def _max_gain_for_attr(rows, attr):
    values = {r[attr] for r in rows}
    total = len(rows)
    labels = {r["label"] for r in rows}
    base = _entropy([sum(1 for r in rows if r["label"] == l) for l in labels])
    best_gain, best_split = -1.0, None
    for candidate in sorted(values, reverse=True):
        left = [r for r in rows if r[attr] == candidate]
        right = [r for r in rows if r[attr] != candidate]
        if not left or not right:
            continue
        mixed = _entropy([sum(1 for r in left if r["label"] == l) for l in labels]) * len(left) / total
        mixed += _entropy([sum(1 for r in right if r["label"] == l) for l in labels]) * len(right) / total
        gain = base - mixed
        if gain > best_gain or (gain == best_gain and candidate > best_split):
            best_gain, best_split = gain, candidate
    return best_gain, best_split


def _entropy(counts):
    total = sum(counts)
    if total == 0:
        return 0.0
    e = 0.0
    for c in counts:
        if c <= 0:
            continue
        p = c / total
        e -= p * (p and __import__("math").log2(p))
    return e


def _build_tree(rows, depth_left):
    if depth_left == 0 or len({r["label"] for r in rows}) == 1:
        return _majority(rows)
    attr, gain, split, _exhausted = _pick_split(rows)
    if attr is None:
        return _majority(rows)
    left = [r for r in rows if r[attr] == split]
    right = [r for r in rows if r[attr] != split]
    return "({}: {}, {})".format(
        attr,
        _build_tree(left, depth_left - 1),
        _build_tree(right, depth_left - 1),
    )


def _majority(rows):
    from collections import Counter
    return max(Counter(r["label"] for r in rows).items(), key=lambda kv: kv[1])[0]


def _build_and_predict(rows, depth_left, order):
    order = list(order)
    if depth_left == 0 or len({r["label"] for r in rows}) == 1:
        cls = _majority(rows)
        pred = {id(r): cls for r in rows}
        return cls, pred
    attr, gain, split, _exhausted = _pick_split(rows)
    if attr is None:
        cls = _majority(rows)
        pred = {id(r): cls for r in rows}
        return cls, pred
    left = [r for r in order if r[attr] == split]
    right = [r for r in order if r[attr] != split]
    lt, lp = _build_and_predict(left, depth_left - 1, left)
    rt, rp = _build_and_predict(right, depth_left - 1, right)
    pred = {}
    pred.update(lp)
    pred.update(rp)
    return "({}: {}, {})".format(attr, lt, rt), pred


@dataclass
class DecisionTreeConfig(Config):
    n_rows: int = 10
    n_labels: int = 2
    attr_pool: int = 3

    def apply_difficulty(self, level):
        self.n_rows = 10 + level * 4
        self.n_labels = 2 + (level >= 2)
        self.attr_pool = 3 + (level >= 2) + (level >= 5)


class DecisionTreeInduction(Task):
    summary = "Build a decision tree by recursive splitting of a small categorical dataset: pick the maximum information-gain attribute per node, with exact count comparisons and fixed tie order; answer is the nested tree."
    design_choice = "Represent the tree as a balanced parenthesized string with attribute names and leaf labels, e.g., (A: x, y) where leaves are class labels."
    config_cls = DecisionTreeConfig

    def render_prompt(self, metadata):
        return module_render_prompt(metadata)

    def generate_entry(self):
        while True:
            attrs = ATTRS[: self.config.attr_pool]
            n = self.config.n_rows
            n_labels = self.config.n_labels
            labels = ["p" + str(i) for i in range(n_labels)]
            rows = []
            for _ in range(n):
                row = {a: random.choice(["0", "1"]) for a in attrs}
                row["label"] = random.choice(labels if len(rows) > 0 else labels)
                rows.append(row)
            counts = {l: sum(1 for r in rows if r["label"] == l) for l in labels}
            if min(counts.values()) == 0:
                continue
            tree = _build_tree(rows, 3)
            check_tree, _ = _build_and_predict(rows, 3, rows)
            if check_tree == tree:
                metadata = {
                    "attrs": attrs,
                    "labels": labels,
                    "rows": rows,
                    "tree": tree,
                }
                return Entry(metadata=metadata, answer=tree)


def _evaluate(tree, rows):
    check_tree, pred = _build_and_predict(rows, 3, rows)
    if check_tree != tree:
        return "mismatch"
    return "ok"


def module_render_prompt(metadata):
    attrs = ", ".join(metadata["attrs"])
    label_line = ", ".join(metadata["labels"])
    lines = ["Attributes: {}.".format(attrs), "Class labels: {}.".format(label_line)]
    for idx, r in enumerate(metadata["rows"]):
        vals = ", ".join("{}={}".format(a, r[a]) for a in metadata["attrs"])
        lines.append("Row {}: {}; label={}.".format(idx, vals, r["label"]))
    lines.append(
        "Build a decision tree by recursive maximum-information-gain splitting of these "
        "{} rows. At every node choose the available attribute with the largest "
        "information gain; break ties by picking the alphabetically first attribute, then "
        "the larger split value. Stop when all remaining rows share one class or no useful "
        "split exists; a region with mixed labels is labeled by its majority class. "
        "Represent the tree in balanced parentheses: a node is written (Attr: left, right), "
        "as in (B: p0, p1) meaning split on B, left branch class p0 and right branch class p1, "
        "and each branch may itself be a further node or a single class label such as p0 or p1. "
        "What is the tree?".format(len(metadata["rows"]))
    )
    return "\n".join(lines)


def score_answer(answer, entry):
    if not isinstance(answer, str):
        return 0.0
    answer = answer.strip()
    if not answer:
        return 0.0
    if answer == entry.answer:
        return 1.0
    return 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'decision_tree_induction (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/decision_tree_induction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
