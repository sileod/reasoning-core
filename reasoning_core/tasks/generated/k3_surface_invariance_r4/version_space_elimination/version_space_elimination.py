"""Version-space elimination (candidate elimination) over a fixed taxonomy tree.

Each feature's 8 leaves (0-7) sit in a fixed binary taxonomy:
  8={0,1} 9={2,3} 10={4,5} 11={6,7}      (groups of 2)
  12={0,1,2,3} 13={4,5,6,7}              (groups of 4)
  14={0,1,2,3,4,5,6,7}                   (top, all 8)
A conjunctive hypothesis assigns every feature a group (a node id); a "box" is a
tuple of groups, one per feature.  It covers an instance (a tuple of leaf ids) if
each feature's group contains that feature's leaf.  The version space is the set
of consistent boxes, and S / G are its most-specific / most-general boundary boxes.
"""

import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'version_space_elimination (variant 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_surface_invariance_r4/version_space_elimination',
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

_TREE_CHILDREN = {8: (0, 1), 9: (2, 3), 10: (4, 5), 11: (6, 7),
                  12: (8, 9), 13: (10, 11), 14: (12, 13)}
_ALL_NODES = list(range(15))


def _group_leafset(node):
    if node < 8:
        return {node}
    l, r = _TREE_CHILDREN[node]
    return _group_leafset(l) | _group_leafset(r)


def _parent(node):
    for p, (l, r) in _TREE_CHILDREN.items():
        if l == node or r == node:
            return p
    return None


def _ancestors(node):
    res = [node]
    p = _parent(node)
    while p is not None:
        res.append(p)
        p = _parent(p)
    return res


def _box_covers(box, inst):
    for g, leaf in zip(box, inst):
        if leaf not in _group_leafset(g):
            return False
    return True


def _gen_boxes(features):
    if features == 0:
        yield ()
    else:
        for g in _ALL_NODES:
            for rest in _gen_boxes(features - 1):
                yield (g,) + rest


def _consistent_boxes(features, positives, negatives):
    res = []
    for box in _gen_boxes(features):
        if all(_box_covers(box, p) for p in positives) and \
           not any(_box_covers(box, n) for n in negatives):
            res.append(box)
    return res


def _box_le(box, other):
    """box pointwise subset-or-equal other (box no more general than other)."""
    return all(_group_leafset(box[i]).issubset(_group_leafset(other[i])) for i in range(len(box)))


def _minimal_boxes(cons):
    return sorted([b for b in cons if not any(o != b and _box_le(o, b) for o in cons)])


def _maximal_boxes(cons):
    return sorted([b for b in cons if not any(o != b and _box_le(b, o) for o in cons)])


def _forced_label(cons, query):
    if not cons:
        return "unknown"
    nc = sum(1 for b in cons if _box_covers(b, query))
    if nc == len(cons):
        return "positive"
    if nc == 0:
        return "negative"
    return "unknown"


def _format_box(box):
    return "(" + ", ".join(str(x) for x in box) + ")"


class VersionSpaceConfig(Config):
    features: int = 2
    trail: int = 4

    def apply_difficulty(self, level):
        self.features = 2 + (level >= 3) + (level >= 5)
        self.trail = 3 + level


class VersionSpaceElimination(Task):
    summary = ("Candidate-elimination over a fixed per-feature taxonomy tree: labeled "
               "leaf-tuple instances arrive, S/G conjunctive boundary boxes are maintained "
               "and reported, and a new instance's label is asked as forced-positive, "
               "forced-negative, or unknown.")
    design_choice = ("Represent attributes as a fixed taxonomy tree per feature, with "
                     "instances as leaf-node tuples; boundaries track the most-specific and "
                     "most-general consistent conjunctions over that tree.")
    config_cls = VersionSpaceConfig

    def generate_entry(self):
        f = self.config.features
        while True:
            s = tuple(random.randint(0, 7) for _ in range(f))
            g = []
            for i in range(f):
                anc = [a for a in _ancestors(s[i]) if a != 14]
                if not anc:
                    anc = _ancestors(s[i])
                g.append(random.choice(anc))
            g = tuple(g)
            if not all(_group_leafset(s[i]).issubset(_group_leafset(g[i])) for i in range(f)):
                continue
            if g == s:
                continue
            pos = [s]
            neg = []
            for i in range(f):
                gi = g[i]
                parent = _parent(gi) if gi >= 8 else None
                if parent is not None:
                    l, r = _TREE_CHILDREN[parent]
                    sib = r if l == gi else l
                    leaf_choices = sorted(_group_leafset(sib))
                    if leaf_choices:
                        ex = list(s)
                        ex[i] = random.choice(leaf_choices)
                        neg.append(tuple(ex))
            if not neg:
                continue
            cons = _consistent_boxes(f, pos, neg)
            if not cons:
                continue
            mins = _minimal_boxes(cons)
            maxs = _maximal_boxes(cons)
            if len(mins) == 1 and len(maxs) == 1 and mins[0] == s and maxs[0] == g:
                break

        mode = random.choice(["s_boundary", "g_boundary", "forced"])
        if mode == "s_boundary":
            ans = _format_box(mins[0])
            query = None
        elif mode == "g_boundary":
            ans = _format_box(maxs[0])
            query = None
        else:
            reg = random.choice(["positive", "negative", "unknown"])
            attempts = 0
            while True:
                attempts += 1
                if reg == "positive":
                    q = s
                elif reg == "negative":
                    q = tuple(random.randint(0, 7) for _ in range(f))
                    if _box_covers(g, q):
                        continue
                else:
                    q = list(s)
                    i = random.randrange(f)
                    avail = sorted(_group_leafset(g[i]))
                    other = [x for x in avail if x != s[i]]
                    if not other:
                        continue
                    q[i] = random.choice(other)
                    q = tuple(q)
                    if q == s:
                        continue
                if _forced_label(cons, q) == reg:
                    break
                if attempts > 200:
                    reg = random.choice(["positive", "negative", "unknown"])
                    attempts = 0
            ans = reg
            query = q

        metadata = {
            "features": f,
            "s": s,
            "g": g,
            "positives": pos,
            "negatives": neg,
            "mode": mode,
            "answer": ans,
            "query": query,
        }
        return Entry(metadata=metadata, answer=ans)

    def render_prompt(self, metadata):
        tree = "; ".join(f"{k}={{{','.join(map(str, sorted(v)))}}}"
                         for k, v in {k: _group_leafset(k) for k in (8, 9, 10, 11, 12, 13, 14)}.items())
        lines = [
            "Each feature has 8 leaves (0-7) joined by a fixed binary taxonomy tree.",
            "Group contents: " + tree + " (leaves 0-7 are singletons; 14 is all 8).",
            "A conjunctive hypothesis assigns each feature one group and covers an instance "
            "(a tuple of leaves) if every feature's group contains its leaf.",
            "You receive labeled examples and maintain the version-space boundaries: "
            "S = most-specific consistent hypotheses, G = most-general consistent ones.",
            "Examples:",
        ]
        for ex in metadata["positives"]:
            lines.append("  instance " + _format_box(ex) + " -> POSITIVE")
        for ex in metadata["negatives"]:
            lines.append("  instance " + _format_box(ex) + " -> NEGATIVE")
        m = metadata["mode"]
        if m == "s_boundary":
            lines.append("What is the most-specific consistent boundary S? Give it as one "
                         "tuple of group ids, e.g. (5, 2).")
        elif m == "g_boundary":
            lines.append("What is the most-general consistent boundary G? Give it as one "
                         "tuple of group ids, e.g. (14, 10).")
        else:
            lines.append("Now a new instance appears: " + _format_box(metadata["query"]) + ".")
            lines.append("Is its label forced to be positive, forced to be negative, or still "
                         "unknown? Answer with exactly one word: positive, negative, or unknown.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return _score_answer(answer, entry)


def _score_answer(answer, entry):
    m = entry.metadata
    mode = m["mode"]
    target = answer.strip()
    if mode in ("s_boundary", "g_boundary"):
        is_s = mode == "s_boundary"
        gold = _format_box(m["s"] if is_s else m["g"])
        return 1.0 if target == gold else 0.0
    # forced
    if target not in ("positive", "negative", "unknown"):
        return 0.0
    return 1.0 if target == m["answer"] else 0.0
