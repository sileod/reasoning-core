import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'tree_subset_counting_dp (draw 2 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/tree_subset_counting_dp',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3577985643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

DESIGN_CHOICE = ("Answer form: exact integer for small n, or modulo a given prime for "
                 "large n, with the prime provided per instance.")

PRIMES = [1000000007, 998244353, 1000000009, 999999937]

VARIANTS = [
    ("independent_set",
     "a set of vertices no two of which are joined by an edge",
     "independent sets"),
    ("matching",
     "a set of edges no two of which share a vertex",
     "matchings"),
    ("vertex_cover",
     "a set of vertices that touches every edge (every edge has at least one"
     " endpoint in the set)",
     "vertex covers"),
]


def _build_tree(n):
    children = [[] for _ in range(n)]
    parents = [None] * n
    for v in range(1, n):
        p = random.randint(0, v - 1)
        parents[v] = int(p)
        children[p].append(v)
    return children, parents


def _edges_from_parents(parents):
    return [(int(p), v) for v, p in enumerate(parents) if p is not None]


def _mul(a, b, mod):
    if mod is None:
        return a * b
    return (a * b) % mod


def _add(a, b, mod):
    if mod is None:
        return a + b
    return (a + b) % mod


def _dp(children, variant, mod):
    n = len(children)
    if variant == "independent_set":
        dp0 = [0] * n
        dp1 = [0] * n
        for v in range(n - 1, -1, -1):
            p0 = 1
            p1 = 1
            for c in children[v]:
                p0 = _mul(p0, _add(dp0[c], dp1[c], mod), mod)
                p1 = _mul(p1, dp0[c], mod)
            dp0[v] = p0
            dp1[v] = p1
        return _add(dp0[0], dp1[0], mod)
    if variant == "vertex_cover":
        dnot = [0] * n
        din = [0] * n
        for v in range(n - 1, -1, -1):
            a0 = 1
            a1 = 1
            for c in children[v]:
                a0 = _mul(a0, din[c], mod)
                a1 = _mul(a1, _add(dnot[c], din[c], mod), mod)
            dnot[v] = a0
            din[v] = a1
        return _add(dnot[0], din[0], mod)
    free = [0] * n
    match = [0] * n
    for v in range(n - 1, -1, -1):
        ch = children[v]
        k = len(ch)
        if k == 0:
            free[v] = 1 if mod is None else 1 % mod
            match[v] = 0
            continue
        total = 1
        for c in ch:
            total = _mul(total, _add(free[c], match[c], mod), mod)
        free[v] = total
        pref = [1] * (k + 1)
        for i in range(k):
            c = ch[i]
            pref[i + 1] = _mul(pref[i], _add(free[c], match[c], mod), mod)
        suff = [1] * (k + 1)
        for i in range(k - 1, -1, -1):
            c = ch[i]
            suff[i] = _mul(suff[i + 1], _add(free[c], match[c], mod), mod)
        inc = 0
        for i in range(k):
            c = ch[i]
            term = _mul(pref[i], suff[i + 1], mod)
            term = _mul(term, free[c], mod)
            inc = _add(inc, term, mod)
        match[v] = inc
    return _add(free[0], match[0], mod)


def _bruteforce(children, parents, variant):
    n = len(children)
    edges = _edges_from_parents(parents)
    out = 0
    if variant == "independent_set":
        for mask in range(1 << n):
            adj = False
            for a, b in edges:
                if (mask >> a) & 1 and (mask >> b) & 1:
                    adj = True
                    break
            if not adj:
                out += 1
    elif variant == "matching":
        m = len(edges)
        for mask in range(1 << m):
            used = set()
            ok = True
            for i in range(m):
                if (mask >> i) & 1:
                    a, b = edges[i]
                    if a in used or b in used:
                        ok = False
                        break
                    used.add(a)
                    used.add(b)
            if ok:
                out += 1
    else:
        for mask in range(1 << n):
            cov = True
            for a, b in edges:
                if not ((mask >> a) & 1 or (mask >> b) & 1):
                    cov = False
                    break
            if cov:
                out += 1
    return out


@dataclass
class TreeSubsetConfig(Config):
    mod_threshold: int = 13

    def apply_difficulty(self, level):
        self.mod_threshold = 13 + 0


class TreeSubsetCounting(Task):
    summary = ("Count independent sets, matchings, and vertex covers of a rooted tree by "
               "bottom-up per-node dynamic programming, exact for small n or modulo a "
               "given prime for large n; the answer is the root count.")
    design_choice = DESIGN_CHOICE
    config_cls = TreeSubsetConfig

    def generate_entry(self):
        level = self.config.level
        lo = 4 + level
        hi = 6 + 5 * level
        n = random.randint(lo, hi)
        for _ in range(50):
            variant_name, variant_desc, plural = random.choice(VARIANTS)
            children, parents = _build_tree(n)
            mod = None
            if n > self.config.mod_threshold:
                mod = random.choice(PRIMES)
            ans = _dp(children, variant_name, mod)
            if ans is None:
                continue
            if n <= self.config.mod_threshold:
                expected = _bruteforce(children, parents, variant_name)
                if expected != ans:
                    raise RuntimeError(
                        f"DP mismatch for n={n} variant={variant_name}: dp={ans} "
                        f"brute={expected}")
                if not (isinstance(ans, int) and ans >= 0):
                    continue
            else:
                if not (isinstance(ans, int) and 0 <= ans < mod):
                    raise RuntimeError(f"mod answer out of range: {ans}")
            return Entry(
                metadata={
                    "n": n,
                    "variant": variant_name,
                    "variant_desc": variant_desc,
                    "plural": plural,
                    "parents": parents,
                    "mod": mod,
                },
                answer=str(ans),
            )
        raise RuntimeError("failed to generate a valid tree instance")

    def render_prompt(self, metadata):
        n = metadata["n"]
        parents = metadata["parents"]
        parent_pairs = ", ".join(
            f"{v}->{parents[v]}" for v in range(1, n) if parents[v] is not None
        )
        node_list = ", ".join(str(v) for v in range(n))
        mod = metadata["mod"]
        if mod is None:
            regime = "the exact number (a non-negative integer)"
        else:
            regime = f"the number modulo {mod}, giving one integer in {{0, 1, ..., {mod - 1}}}"
        return (
            f"We count {metadata['plural']} in a rooted tree with {n} nodes labeled "
            f"{node_list}, root 0. A {metadata['variant'].replace('_', ' ')} is "
            f"{metadata['variant_desc']}. The tree's parent links are ({parent_pairs}). "
            "Compute the count by bottom-up dynamic programming at each node, combining "
            "child subtrees into one count per node. Report " + regime +
            ". The answer is a single integer with no extra text."
        )

    def score_answer(self, answer, entry):
        ref = entry["answer"]
        try:
            a = int(str(answer).strip())
            r = int(str(ref).strip())
        except (ValueError, TypeError):
            return 0.0
        return 1.0 if a == r else 0.0



