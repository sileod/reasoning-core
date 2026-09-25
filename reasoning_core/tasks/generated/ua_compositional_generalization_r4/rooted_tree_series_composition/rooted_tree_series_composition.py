"""Compose two rooted-tree-indexed formal series via admissible cuts and forests.

The coefficient of a queried rooted tree in the composition A circ B is a sum
over every admissible cut of that tree, the pruned (root) component weighted by
A and the remaining forest weighted by the product of B over its components,
divided by the forest automorphism factor. Coefficients are reported as reduced
fractions (the unordered-species normalization introduces denominators even from
integer-valued input series).
"""

import random
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from fractions import Fraction
from itertools import product

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
             'idea': 'rooted_tree_series_composition (variant 1 of 3)',
             'hypothesis': 'P011',
             'changes': 'new task in '
                        'reasoning_core/tasks/generated/ua_compositional_generalization_r4/rooted_tree_series_composition',
             'generation': {'provider_name': 'albert',
                            'model_name': 'deepseek-v4-flash',
                            'harness_name': 'opencode',
                            'harness_version': '1.18.32',
                            'agent_name': 'task-search-worker',
                            'settings': {'variant': None,
                                         'requested_seed': 2305351643,
                                         'seed_forwarded': True,
                                         'temperature': None,
                                         'top_p': None,
                                         'pure': True,
                                         'max_steps': 56,
                                         'timeout_seconds': 1800,
                                         'sandbox': {'name': 'bubblewrap',
                                                     'version': 'bubblewrap 0.8.0'}}}}


def canonical_string(t):
    if not t:
        return "o"
    return "(" + "".join(sorted(canonical_string(c) for c in t)) + ")"


def aut_forest(forest):
    c = Counter(forest)
    v = 1
    for m in c.values():
        for i in range(2, m + 1):
            v *= i
    return v


@lru_cache(maxsize=None)
def forests(n):
    if n <= 0:
        return ((),)
    res = set()
    for s in range(1, n + 1):
        for tr in trees(s):
            for rest in forests(n - s):
                res.add(tuple(sorted(list(rest) + [tr], key=canonical_string)))
    return tuple(res)


@lru_cache(maxsize=None)
def trees(n):
    if n <= 1:
        return ((),)
    res = set()
    for f in forests(n - 1):
        res.add(tuple(f))
    return tuple(res)


def all_trees_upto(n):
    out = []
    for k in range(1, n + 1):
        lst = list(trees(k))
        lst.sort(key=canonical_string)
        out.extend(lst)
    return out


def cuts(t):
    """All admissible cuts; returns list of (pruned_canonical, forest_tuple)."""
    if not t:
        return [((), ())]
    options = []
    for child in t:
        opts = [(True, child)]  # cut this edge: subtree removed whole
        for sp, sf in cuts(child):
            opts.append((False, sp, sf))
        options.append(opts)
    seen = set()
    out = []
    for combo in product(*options):
        kept = []
        forest = []
        for entry in combo:
            if entry[0]:
                forest.append(entry[1])
            else:
                kept.append(entry[1])
                forest.extend(entry[2])
        pruned = tuple(sorted(kept, key=canonical_string))
        fsorted = tuple(sorted(forest, key=canonical_string))
        key = (pruned, fsorted)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _subtrees_occurrences(t):
    occ = []
    def walk(x):
        occ.append(x)
        for c in x:
            walk(c)
    walk(t)
    return occ


def brute_cuts(t):
    """Independent admissible-cut enumeration over all edge subsets."""
    counter = [0]
    def build(x):
        nid = counter[0]
        counter[0] += 1
        kids = [(build(c)) for c in x]
        return (nid, kids)
    root_id, root_children = build(t)
    children = {}
    parent = {}
    def register(nid, kids, par):
        children[nid] = kids
        parent[nid] = par
        for cid, sub in kids:
            register(cid, sub, nid)
    register(root_id, root_children, None)
    all_ids = list(children.keys())
    edges = []
    for nid in all_ids:
        if nid != root_id:
            edges.append((parent[nid], nid))
    anc = {}
    for nid in all_ids:
        a = set()
        p = parent[nid]
        while p is not None:
            a.add(p)
            p = parent[p]
        anc[nid] = a
    edge_childids = [c for (_, c) in edges]
    result = set()
    ne = len(edges)
    for mask in range(1 << ne):
        cutset = []
        ok = True
        for i in range(ne):
            if (mask >> i) & 1:
                c = edge_childids[i]
                for d in cutset:
                    if c in anc[d] or d in anc[c]:
                        ok = False
                        break
                if not ok:
                    break
                cutset.append(c)
        if not ok:
            continue
        Cset = set(cutset)
        def canon(nid, exclude):
            parts = sorted(
                (canon(cid, exclude) for (cid, _) in children[nid] if cid not in exclude),
                key=canonical_string)
            return tuple(parts)
        pruned = canon(root_id, Cset)
        forest = tuple(sorted((canon(c, set()) for c in Cset), key=canonical_string))
        result.add((pruned, forest))
    return result


def compose(A, B, t, cut_fn):
    total = Fraction(0, 1)
    for pruned, forest in cut_fn(t):
        av = A.get(pruned, 0)
        if not av:
            continue
        bp = 1
        for s in forest:
            bv = B.get(s, 0)
            if not bv:
                bp = 0
                break
            bp *= bv
        if not bp:
            continue
        total += Fraction(av * bp, aut_forest(forest))
    return total


def random_partition_sum(s, k):
    if k <= 1:
        return [s]
    cuts = sorted(random.sample(range(1, s), k - 1))
    out = []
    prev = 0
    for c in cuts + [s]:
        out.append(c - prev)
        prev = c
    return out


def random_canonical_tree(n):
    if n <= 1:
        return ()
    k = random.randint(1, n - 1)
    while k > n - 1:
        k = random.randint(1, n - 1)
    parts = random_partition_sum(n - 1, k)
    return tuple(sorted((random_canonical_tree(ps) for ps in parts), key=canonical_string))


def parse_fraction(s):
    if not isinstance(s, str):
        return None
    try:
        return Fraction(s)
    except (ValueError, ZeroDivisionError):
        return None


@dataclass
class RootedTreeSeriesCompositionConfig(Config):
    series_size: int = 3
    query_min: int = 2
    query_max: int = 2
    max_coeff: int = 1

    def apply_difficulty(self, level):
        self.max_coeff = 1 + level
        self.series_size = min(3 + level, 6)
        self.query_max = max(self.query_min, self.series_size - 1)


class RootedTreeSeriesComposition(Task):
    summary = "Compose two rooted-tree-indexed formal series by summing admissible cuts and forest contributions; vary branching, repeated subtrees, and series size, returning a queried tree coefficient as a reduced fraction."
    design_choice = "Coefficient answer is a reduced fraction; instances vary by composing two series with integer coefficients and querying a tree coefficient that forces nontrivial denominator cancellation."
    config_cls = RootedTreeSeriesCompositionConfig

    def generate_entry(self):
        cfg = self.config
        support = all_trees_upto(cfg.series_size)
        A = {}
        B = {}
        for tr in support:
            A[tr] = random.randint(-cfg.max_coeff, cfg.max_coeff)
            B[tr] = random.randint(-cfg.max_coeff, cfg.max_coeff)
        best = None
        for _ in range(40):
            n = random.randint(cfg.query_min, cfg.query_max)
            qtree = random_canonical_tree(n)
            val1 = compose(A, B, qtree, cuts)
            val2 = compose(A, B, qtree, brute_cuts)
            if val1 != val2:
                raise RuntimeError("admissible-cut enumerators disagree")
            cand = (val1.numerator, val1.denominator)
            if val1.denominator > 1:
                best = cand
                break
            best = cand
        num, den = best
        A_s = {canonical_string(k): v for k, v in A.items()}
        B_s = {canonical_string(k): v for k, v in B.items()}
        answer = str(num) if den == 1 else f"{num}/{den}"
        return Entry(
            metadata={
                "A": A_s,
                "B": B_s,
                "query": canonical_string(qtree),
                "coeff_num": num,
                "coeff_den": den,
                "series_size": cfg.series_size,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        def sfmt(ts):
            return ts

        lines = []
        lines.append(
            "We use rooted trees with unlabeled nodes and unordered children, encoded "
            "canonically: a leaf is `o`, and a node whose children have encodings "
            "c1..ck (in sorted order) is `(c1..ck)`. So the 2-node tree is `(o)` and "
            "a root with three leaf children is `(ooo)`."
        )
        lines.append("")
        lines.append(
            "A tree series assigns an integer coefficient to each finite rooted tree. "
            "Given two integer tree series A and B, the coefficient (A\u2218B)[T] of their "
            "composition on a tree T is the sum, over every admissible cut of T, of "
            "the contribution A[P] * (product of B[s] over forests pieces s in F) / aut(F). "
            "An admissible cut chooses a set of edges no two of which lie on a common "
            "root-to-leaf path; it splits T into a pruned tree P (the part containing "
            "the root) and a forest F of the remaining rooted trees. aut(F) is the "
            "product, over each distinct child-tree appearing m times in F, of m! (the "
            "automorphism factor of the unordered forest). The empty cut (choose no "
            "edges) is included."
        )
        lines.append("")
        lines.append("Series A:")
        for ts in sorted(metadata["A"].keys()):
            lines.append(f"A[{ts}] = {metadata['A'][ts]}")
        lines.append("")
        lines.append("Series B:")
        for ts in sorted(metadata["B"].keys()):
            lines.append(f"B[{ts}] = {metadata['B'][ts]}")
        lines.append("")
        lines.append(f"Query tree Q = {metadata['query']}.")
        lines.append(
            "Compute (A\u2218B)[Q]. Give the answer as a reduced fraction p/q, or as a "
            "plain integer p when it is integral (e.g. -13/6 or 7)."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        frac = parse_fraction(answer)
        if frac is None:
            return 0.0
        gold = Fraction(entry.metadata["coeff_num"], entry.metadata["coeff_den"])
        return 1.0 if frac == gold else 0.0
