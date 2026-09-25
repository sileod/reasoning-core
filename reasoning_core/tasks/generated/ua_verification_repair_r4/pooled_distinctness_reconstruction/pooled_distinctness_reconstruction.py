import random
from dataclasses import dataclass
from functools import lru_cache

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'pooled_distinctness_reconstruction (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_verification_repair_r4/pooled_distinctness_reconstruction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3536382515,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def all_partitions(n):
    """All set partitions of range(n) as tuples of sorted blocks (restricted growth)."""
    if n == 0:
        return ((),)
    res = []
    a = [0] * n

    def rec(i):
        if i == n:
            blocks = {}
            for x, v in enumerate(a):
                blocks.setdefault(v, []).append(x)
            res.append(tuple(sorted([tuple(b) for b in blocks.values()])))
            return
        maxv = max(a[:i])
        for v in range(maxv + 2):
            a[i] = v
            rec(i + 1)

    rec(1)
    return tuple(res)


@lru_cache(maxsize=None)
def _cached_partitions(n):
    return all_partitions(n)


def compute_forced(n, pools):
    """Given items 0..n-1 and pools [[items, kind, value]...], return (same_pairs, diff_pairs)
    where a pair is FORCED SAME if every consistent typing keeps them together and FORCED
    DIFFERENT if every consistent typing keeps them apart. A typing is an item->type map
    consistent with every pool report."""
    maps = []
    for p in _cached_partitions(n):
        mp = {}
        for bi, blk in enumerate(p):
            for x in blk:
                mp[x] = bi
        maps.append(mp)

    consistent = []
    for mp in maps:
        ok = True
        for items, kind, value in pools:
            d = len({mp[x] for x in items})
            if kind == '=' and d != value:
                ok = False
                break
            if kind == '<=' and d > value:
                ok = False
                break
            if kind == '>=' and d < value:
                ok = False
                break
        if ok:
            consistent.append(mp)

    same = set()
    diff = set()
    ncons = len(consistent)
    for a in range(n):
        for b in range(a + 1, n):
            s = sum(1 for mp in consistent if mp[a] == mp[b])
            d = sum(1 for mp in consistent if mp[a] != mp[b])
            if s == ncons:
                same.add((a, b))
            if d == ncons:
                diff.add((a, b))
    return sorted(same), sorted(diff)


def _build_pools(n, n_pools, types):
    pools = []
    a, b = sorted(random.sample(range(n), 2))
    pools.append([[a, b], '=', len({types[a], types[b]})])
    for _ in range(n_pools - 1):
        size = random.randint(2, n)
        items = sorted(random.sample(range(n), size))
        c = len({types[x] for x in items})
        kind = random.choice(['=', '<=', '>='])
        if kind == '=':
            value = c
        elif kind == '<=':
            hi = size - 1
            if hi < c:
                hi = c
            value = random.randint(c, hi)
        else:
            lo = 1
            if lo > c:
                lo = c
            value = random.randint(lo, c)
        pools.append([items, kind, value])
    return pools


def _answer_string(same_pairs, diff_pairs):
    left = str([[a, b] for a, b in same_pairs])
    right = str([[a, b] for a, b in diff_pairs])
    return f"{left} and {right}"


@dataclass
class PooledDistinctnessConfig(Config):
    n_items: int = 4
    n_pools: int = 3

    def apply_difficulty(self, level):
        self.n_items = min(self.n_items + level, 7)
        self.n_pools = min(self.n_pools + level, 9)


class PooledDistinctnessReconstruction(Task):
    summary = ("Overlapping pools report exact, bounded, or saturated counts of distinct hidden "
               "types rather than item counts; reconcile one global partition and recover forced "
               "same-type and different-type item pairs.")
    design_choice = ("Answer format: a canonical sorted list of forced same-type pairs and "
                     "different-type pairs, e.g., [[a,b],[c,d]] and [[e,f]]")
    config_cls = PooledDistinctnessConfig
    task_version = 2

    def generate_entry(self):
        n = self.config.n_items
        n_pools = self.config.n_pools
        for _ in range(50):
            n_types = random.randint(1, min(3, max(1, n - 1)))
            types = [random.randrange(n_types) for _ in range(n)]
            pools = _build_pools(n, n_pools, types)
            same_pairs, diff_pairs = compute_forced(n, pools)
            if len(same_pairs) + len(diff_pairs) >= 1:
                answer = _answer_string(same_pairs, diff_pairs)
                metadata = {
                    "item_ids": list(range(n)),
                    "pools": pools,
                    "hidden_types": types,
                    "forced_same": same_pairs,
                    "forced_diff": diff_pairs,
                }
                return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("pooled_distinctness_reconstruction: no non-trivial forced pair found")

    def render_prompt(self, metadata):
        items = metadata['item_ids']
        lines = []
        for idx, (plist, kind, value) in enumerate(metadata['pools'], start=1):
            if kind == '=':
                desc = f"exactly {value} distinct type{'s' if value != 1 else ''}"
            elif kind == '<=':
                desc = f"at most {value} distinct types"
            else:
                desc = f"at least {value} distinct types"
            lines.append(f"Pool {idx}: items {{{', '.join(str(x) for x in plist)}}} -- {desc}.")
        pools_txt = "\n".join(lines)
        return (
            f"The items are labeled by the IDs {sorted(items)}. Each item carries a hidden "
            f"\"type\" (two items with the same type are indistinguishable). Several overlapping "
            f"pools -- subsets of items -- are given; each pool reports a count about the "
            f"distinct types present among its members, and every pool either reports the exact "
            f"number of distinct types, an upper bound (at most), or a lower bound (at least). "
            f"A \"consistent typing\" assigns a type to every item so that every pool report "
            f"holds; at least one such typing exists.\n\n"
            f"The pools are:\n{pools_txt}\n\n"
            f"Two items are FORCED SAME when every consistent typing places them in the same "
            f"type, and FORCED DIFFERENT when every consistent typing places them in different "
            f"types.\n\n"
            f"List every forced same-type pair and every forced different-type pair. Write each "
            f"pair as a two-item list a<b. Give the answer as two sorted lists: the list of "
            f"forced same pairs, then the word \"and\", then the list of forced different pairs; "
            f"use [] for an empty list. Example of the format: [[0, 3], [1, 2]] and [[0, 1]]."
        )

    def score_answer(self, answer, entry):
        if str(answer).strip() == str(entry.answer).strip():
            return 1.0
        return 0.0
