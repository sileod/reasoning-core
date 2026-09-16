import random

from reasoning_core.template import Task, Entry, Config, edict, render_payload


TASK_META = {'parent_source_id': None,
 'idea': 'interval_nesting_forest (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/interval_nesting_forest',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class IntervalNestingForestConfig(Config):
    n: int = 5
    max_val: int = 60
    depth: int = 2

    def apply_difficulty(self, level):
        self.n = 5 + 2 * level
        self.depth = 2 + level


def _build_intervals(n, max_val, depth):
    """Return a list of distinct intervals (l, r) with 0 <= l < r <= max_val.

    Nested structure is guaranteed by first laying down a shrinking spine, then
    adding random side intervals that may nest or sit alongside them.
    """
    intervals = []
    seen = set()

    def add(l, r):
        if 0 <= l < r <= max_val and (l, r) not in seen:
            seen.add((l, r))
            intervals.append((l, r))
            return True
        return False

    lo = random.randint(0, max_val // 4)
    hi = random.randint(3 * max_val // 4, max_val)
    if hi - lo < 4:
        hi = max_val
        lo = 0
    cur_l, cur_r = lo, max(hi, lo + 4)
    add(cur_l, cur_r)
    for _ in range(depth - 1):
        if cur_r - cur_l < 5:
            break
        mid = (cur_l + cur_r) // 2
        new_l = random.randint(cur_l + 1, mid)
        new_r = random.randint(mid + 1, cur_r - 1)
        if new_l < new_r:
            add(new_l, new_r)
            cur_l, cur_r = new_l, new_r

    guard = 0
    while len(intervals) < n and guard < 2000:
        guard += 1
        l = random.randint(0, max_val - 2)
        w = random.randint(1, max_val - l - 1)
        add(l, l + w)
    return intervals


def _compute_parents(intervals):
    n = len(intervals)
    parents = [-1] * n
    for i in range(n):
        li, ri = intervals[i]
        best = -1
        best_key = None
        for j in range(n):
            if j == i:
                continue
            lj, rj = intervals[j]
            if lj < li and ri < rj:
                key = ((rj - lj), lj)
                if best_key is None or key < best_key:
                    best_key = key
                    best = j
        parents[i] = best
    return parents


def _preorder(intervals, parents):
    n = len(intervals)
    children = [[] for _ in range(n)]
    roots = []
    for i in range(n):
        if parents[i] == -1:
            roots.append(i)
        else:
            children[parents[i]].append(i)

    def order_key(i):
        return (intervals[i][0], i)

    roots.sort(key=order_key)
    for c in children:
        c.sort(key=order_key)

    result = []

    def dfs(u):
        result.append(u)
        for v in children[u]:
            dfs(v)

    for r in roots:
        dfs(r)
    return result


def _verify(intervals, parents, preorder):
    n = len(intervals)
    recomputed = _compute_parents(intervals)
    assert recomputed == parents, "parent computation must be reproducible"
    assert sorted(preorder) == list(range(n)), "preorder must be a permutation of all IDs"
    position = {v: idx for idx, v in enumerate(preorder)}
    for i in range(n):
        if parents[i] != -1:
            assert position[parents[i]] < position[i], "parent must precede child in preorder"
    return True


def _parse_ids(answer):
    try:
        parts = [p.strip() for p in str(answer).split(",") if p.strip()]
        return [int(p) for p in parts]
    except ValueError:
        return None


class IntervalNestingForest(Task):
    summary = ("Containment forest over integer intervals within a fixed range: "
               "parent is the tightest strict container under leftmost-tie-break, "
               "canonical leftmost-first root/child ordering; answer is the DFS preorder ID string")
    design_choice = ("Vary interval endpoints as integers within a fixed range, with explicit "
                     "tie-breaking rules for equal endpoints (leftmost-first), and encode the "
                     "forest as a depth-first preorder string of interval IDs.")
    config_cls = IntervalNestingForestConfig

    def generate_entry(self):
        n = self.config.n
        max_val = self.config.max_val
        depth = self.config.depth
        for _ in range(2000):
            intervals = _build_intervals(n, max_val, depth)
            if len(intervals) < 3:
                continue
            parents = _compute_parents(intervals)
            n_nonroot = sum(1 for p in parents if p != -1)
            if n_nonroot < max(1, n // 4):
                continue
            preorder = _preorder(intervals, parents)
            _verify(intervals, parents, preorder)
            break
        else:
            raise RuntimeError("could not build a non-trivial interval forest")

        metadata = edict({
            'intervals': [[int(l), int(r)] for l, r in intervals],
            'max_val': int(max_val),
            'parents': [int(p) for p in parents],
            'preorder': [int(v) for v in preorder],
        })
        metadata.payload = {
            'label': 'IDs are 0-indexed in this listing order',
            'intervals': '\n'.join(
                f"{i}: [{l}, {r}]" for i, (l, r) in enumerate(intervals)
            ),
        }
        return Entry(metadata=metadata, answer=",".join(str(v) for v in preorder))

    def render_prompt(self, metadata):
        body = render_payload(metadata.payload)
        head = (
            "Here is a set of integer intervals, each labeled with an ID (0-indexed "
            "in the listing order):\n\n"
            f"{body}\n\n"
            "Build the containment forest as follows. Interval J strictly contains "
            "interval I when l_J < l_I and r_I < r_J. The parent of an interval is the "
            "strict container with the smallest width (r_J - l_J); if several tie on "
            "width, pick the one with the smaller left endpoint (leftmost tie-break). "
            "Intervals with no strict container are roots.\n\n"
            "Report the forest as a depth-first preorder traversal string. Visit the "
            "roots in increasing order of left endpoint (ties broken by increasing ID), "
            "and within each node visit its children in increasing left endpoint (ties "
            "broken by increasing ID). Output the ID of each interval the first time it "
            "is visited, all IDs separated by commas. Parents always appear before "
            "their descendants, and every ID appears exactly once.\n\n"
            "Answer with only the comma-separated preorder ID list."
        )
        return head

    def score_answer(self, answer, entry):
        parsed = _parse_ids(answer)
        if parsed is None:
            return 0.0
        return 1.0 if parsed == list(entry.metadata.preorder) else 0.0
