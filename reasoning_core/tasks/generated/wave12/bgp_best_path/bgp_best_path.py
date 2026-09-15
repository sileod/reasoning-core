"""BGP best-path selection from a tabular route attribute set."""

import random

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'bgp_best_path (draw 1 of 3)',
 'hypothesis': 'external:bgp_best_path',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/bgp_best_path',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2401670496,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def best_path(rows):
    """Apply the BGP best-path rule sequence, return index of winner.

    Rules in order:
      1. highest local preference (higher is better)
      2. shortest AS path length (shorter is better)
      3. lowest origin (IGP=0 < EGP=1 < incomplete=2)
      4. lowest MED (lower is better; -1 means unset, treated as largest)
      5. lowest router ID (used only when the above four all tie)
    Every decisive tie falls through to the next rule, so exactly one row wins.
    """
    best = 0
    for i in range(1, len(rows)):
        a = rows[best]
        b = rows[i]
        if _better(b, a):
            best = i
    return best


def _better(x, y):
    return (
        (x['localpref'] > y['localpref']) or
        (x['localpref'] == y['localpref'] and x['aspath_len'] < y['aspath_len']) or
        (x['localpref'] == y['localpref'] and x['aspath_len'] == y['aspath_len']
         and x['origin'] < y['origin']) or
        (x['localpref'] == y['localpref'] and x['aspath_len'] == y['aspath_len']
         and x['origin'] == y['origin'] and _med_lt(x['med'], y['med'])) or
        (x['localpref'] == y['localpref'] and x['aspath_len'] == y['aspath_len']
         and x['origin'] == y['origin'] and x['med'] == y['med']
         and x['router_id'] < y['router_id'])
    )


def _med_lt(a, b):
    if a == b:
        return False
    if a == -1:
        return False
    if b == -1:
        return True
    return a < b


class BgpBestPathConfig(Config):
    n_rows: int = 4

    def apply_difficulty(self, level):
        self.n_rows = stochastic_rounding(4 + level * 2)


class BgpBestPath(Task):
    summary = ("Given BGP route attributes, output the route selected by a stated "
               "best-path rule sequence; tabular rows with localpref, AS path "
               "length, origin, MED and router ID, selecting one winning row index.")
    config_cls = BgpBestPathConfig
    design_choice = ("Route attributes are presented as a table with columns for "
                     "localpref, AS path length, origin, MED, and router ID; the "
                     "answer is the index of the winning row.")

    def generate_entry(self):
        n = self.config.n_rows
        while True:
            rows = []
            for _ in range(n):
                rows.append({
                    'localpref': random.randint(0, 200),
                    'aspath_len': random.randint(1, 12),
                    'origin': random.choice([0, 1, 2]),
                    'med': random.choice([-1] + list(range(0, 100))),
                    'router_id': random.randint(1, 255),
                })
            res = best_path(rows)
            # Ensure a legitimate domain: the winning index must be in range and
            # reproducible by the verifier. Also ensure the first rule interacts
            # (avoid trivial single-winner-at-top-level degeneracy by checking the
            # winner is not determined solely by a constant).
            if 0 <= res < n:
                return Entry(metadata={'rows': rows}, answer=str(res))

    def render_prompt(self, metadata):
        rows = metadata['rows']
        lines = [
            "A router is choosing between the routes below using the BGP best-path "
            "selection rule sequence, applied in order:",
            "1. highest local preference (higher is better)",
            "2. shortest AS path length (shorter is better)",
            "3. lowest origin (IGP=0, EGP=1, incomplete=2)",
            "4. lowest MED (lower is better; MED=-1 means unset and is treated as "
            "the largest)",
            "5. lowest router ID (only as the final tie-break)",
            "",
            "The routes (index, localpref, AS path length, origin, MED, router ID):",
        ]
        for i, r in enumerate(rows):
            lines.append(
                f"  Row {i}: localpref={r['localpref']}, "
                f"AS path length={r['aspath_len']}, origin={r['origin']}, "
                f"MED={r['med']}, router ID={r['router_id']}")
        lines.append("")
        lines.append("Which route wins? Answer with the single winning index, e.g. 2.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == best_path(entry.metadata['rows']) else 0.0
        except (ValueError, TypeError):
            return 0.0
