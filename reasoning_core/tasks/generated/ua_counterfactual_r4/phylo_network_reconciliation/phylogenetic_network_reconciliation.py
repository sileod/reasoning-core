import random

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'phylogenetic_network_reconciliation (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_counterfactual_r4/phylogenetic_network_reconciliation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = ("Generate two rooted binary trees on a common leaf set where one is built from the "
                 "other by a set of independent single-leaf subtree prune-and-regraft moves; ask for the "
                 "minimum number of reticulation (reticulate) nodes in any network displaying both trees, "
                 "computed exactly by a hybrid-number search.")


# ---------------------------------------------------------------------------
# Canonical tree representation and the exact hybrid-number (minimum
# reticulation count) algorithm for a pair of rooted binary trees on a common
# leaf set.  A leaf is an int; an internal node is a tuple of its subtrees.
# ---------------------------------------------------------------------------

def _token(t):
    if isinstance(t, int):
        return ("L", t)
    return ("N", tuple(sorted((_token(c) for c in t), key=str)))


def _collect(t):
    if isinstance(t, int):
        return [t]
    out = []
    for c in t:
        out.extend(_collect(c))
    return out


def _remove_leaf(t, x):
    if isinstance(t, int):
        return None if t == x else t
    kids = [r for r in (_remove_leaf(c, x) for c in t) if r is not None]
    if not kids:
        return None
    if len(kids) == 1:
        return kids[0]
    return tuple(kids)


def _cherries(t):
    cherries = set()
    if isinstance(t, int):
        return cherries
    for c in t:
        if isinstance(c, tuple) and len(c) == 2 and all(isinstance(z, int) for z in c):
            cherries.add(frozenset(c))
        cherries |= _cherries(c)
    return cherries


def _reduce_common(t1, t2):
    while True:
        common = _cherries(t1) & _cherries(t2)
        if not common:
            return t1, t2
        a, b = tuple(next(iter(common)))
        t1 = _remove_leaf(_remove_leaf(t1, a), b)
        t2 = _remove_leaf(_remove_leaf(t2, a), b)


def _random_tree(leaves, min_cherries):
    while True:
        nodes = list(leaves)
        random.shuffle(nodes)
        while len(nodes) > 1:
            i, k = random.sample(range(len(nodes)), 2)
            a, b = nodes[i], nodes[k]
            if i < k:
                nodes.pop(k)
                nodes.pop(i)
            else:
                nodes.pop(i)
                nodes.pop(k)
            nodes.append((a, b))
        tree = nodes[0]
        if len(_cherries(tree)) >= min_cherries:
            return tree


def _insert_sibling(t, w, newleaf):
    """In nested-tree form, re-insert `newleaf` as a sibling of leaf `w`."""
    if isinstance(t, int):
        if t == w:
            return (newleaf, w)
        return t
    out = []
    for c in t:
        out.append(_insert_sibling(c, w, newleaf))
    return tuple(out)


def build_pair(n, r):
    """Build two trees on n leaves differing by r independent single-leaf moves.
    Returns (t1, t2) as nested tuples, or None if the move selection fails."""
    leaves = list(range(n))
    t1 = _random_tree(leaves, r)
    cherries = sorted(_cherries(t1), key=lambda s: sorted(s))
    if r > len(cherries):
        return None
    random.shuffle(cherries)
    selected = cherries[:r]
    used = set()
    for s in selected:
        used.update(s)
    free = [x for x in leaves if x not in used]
    if len(free) < r:
        return None
    random.shuffle(free)
    anchors = free[:r]

    t2 = t1
    for i in range(r):
        uu, v = tuple(sorted(selected[i]))
        w = anchors[i]
        t2 = _insert_sibling(_remove_leaf(t2, uu), w, uu)
    return t1, t2


def hybrid_number(t1, t2):
    """Exact minimum number of reticulation nodes (hybridization number) of a
    network that displays both rooted binary trees t1 and t2."""
    memo = {}

    def hh(ta, tb):
        key = (_token(ta), _token(tb))
        if key in memo:
            return memo[key]
        ra, rb = _reduce_common(ta, tb)
        if _token(ra) == _token(rb):
            memo[key] = 0
            return 0
        leaves = _collect(ra)
        best = None
        for x in leaves:
            na = _remove_leaf(ra, x)
            nb = _remove_leaf(rb, x)
            cand = 1 + hh(na, nb)
            if best is None or cand < best:
                best = cand
        memo[key] = best
        return best

    return hh(t1, t2)


def _newick(t):
    if isinstance(t, int):
        return str(t)
    inner = ",".join(sorted(_newick(c) for c in t))
    return "(" + inner + ")"


class PhyloReconConfig(Config):
    leaves: int = 6
    rmax: int = 2

    def apply_difficulty(self, level):
        if level <= 1:
            self.leaves = 6
            self.rmax = 2
        elif level <= 3:
            self.leaves = 8
            self.rmax = 2
        elif level <= 5:
            self.leaves = 10
            self.rmax = 3
        else:
            self.leaves = 12
            self.rmax = 4


task_version = 2


class phylo_network_reconciliation(Task):
    summary = ("Combine two rooted trees on a common leaf set into a network displaying both, "
               "reconnecting them through reticulation choices and subdivision suppression; "
               "return the minimum reticulation count of independent leaf hybridizations.")
    config_cls = PhyloReconConfig

    def generate_entry(self):
        n = self.config.leaves
        rmax = self.config.rmax
        rmax = min(rmax, max(1, n // 3))
        while True:
            r = random.randint(1, rmax)
            built = build_pair(n, r)
            if built is None:
                continue
            t1, t2 = built
            h = hybrid_number(t1, t2)
            if h == r and h >= 1:
                return Entry(
                    metadata={
                        "leaves": n,
                        "expected": r,
                        "hybrid": h,
                        "newick1": _newick(t1) + ";",
                        "newick2": _newick(t2) + ";",
                    },
                    answer=str(h),
                )

    def render_prompt(self, metadata):
        return (
            "Two rooted trees on the same set of leaves are given in parenthesized form "
            "(leaves are integers; a node's children are the strings inside its "
            "parentheses). A phylogenetic network can display both trees by letting some "
            "node inherit two parents (a reticulation / reticulate node) and by "
            "suppressing degree-2 nodes. Give the MINIMUM number of reticulation nodes of "
            "any network that displays both trees, as a single non-negative integer "
            "(answer format e.g. '4').\n"
            f"Tree 1: {metadata['newick1']}\n"
            f"Tree 2: {metadata['newick2']}"
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip()
        try:
            av = int(a)
        except ValueError:
            return 0.0
        try:
            gv = int(entry.answer)
        except ValueError:
            return 0.0
        return 1.0 if av == gv else 0.0
