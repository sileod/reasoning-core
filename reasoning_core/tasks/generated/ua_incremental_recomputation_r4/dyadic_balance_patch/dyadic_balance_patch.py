import random
from dataclasses import dataclass
from functools import lru_cache

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'dyadic_balance_patch (variant 1 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/dyadic_balance_patch',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 3867019559,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class DyadicBalancePatchConfig(Config):
    L: int = 8
    S: int = 4

    def apply_difficulty(self, level):
        self.L = 2 ** (level + 2)
        self.S = level + 3


def _min_splits(s, r):
    L = len(s)

    @lru_cache(maxsize=None)
    def dp(start, jj):
        length = 1 << jj
        if length == 1:
            return 1
        mn = min(s[start:start + length])
        if length <= r * mn:
            return 1
        half = length >> 1
        return dp(start, jj - 1) + dp(start + half, jj - 1)

    m = L.bit_length() - 1
    leaves = dp(0, m)
    return leaves - 1


def _score_answer(answer, entry):
    try:
        parsed = int(str(answer).strip())
    except ValueError:
        return 0.0
    return 1.0 if parsed == int(entry.answer) else 0.0


def _render(metadata):
    L = metadata["L"]
    s = metadata["s"]
    r = metadata["r"]
    return (
        f"An oversized strip that is {L} columns wide sits on top of a row of neighbor cells. "
        f"Reading left to right the neighbor cell areas directly below the strip are {s}. "
        f"The strip may be refined only with balanced dyadic bisection: repeatedly pick a current "
        f"strip interval and cut it exactly in half at its midpoint, producing two pieces each of "
        f"half the length. A final strip piece spanning columns [a,b) has length b-a and is allowed "
        f"exactly when its length is at most {r} times the smallest neighbor cell area beneath it, "
        f"i.e. (b-a) <= {r} * (minimum of the listed areas from column a to column b-1). Every "
        f"column must end up in exactly one piece. What is the minimum number of bisection cuts "
        f"needed so that every final strip piece satisfies this neighbor size-ratio limit? "
        f"Answer with the non-negative integer number of cuts only, nothing else."
    )


class DyadicBalancePatch(Task):
    summary = ("Repair dyadic cell partitions after local refinement or coarsening; enforce "
               "face- or corner-neighbor size limits across periodic and bounded domains, "
               "returning the minimal additional subdivisions.")
    design_choice = ("Instances give a 2D grid partition with a single over-sized cell; answer "
                     "is the minimum number of bisection splits needed to satisfy all neighbor "
                     "size ratios, with balanced splits only.")
    config_cls = DyadicBalancePatchConfig

    def generate_entry(self):
        L = self.config.L
        S = self.config.S
        r = random.choice([1, 2, 3])
        s = [random.randint(1, S) for _ in range(L)]
        splits = _min_splits(s, r)
        if splits < 0:
            raise RuntimeError("negative split count")
        return Entry(metadata={"L": L, "s": s, "r": r, "splits": int(splits)},
                     answer=str(int(splits)))

    def render_prompt(self, metadata):
        return _render(metadata)

    def score_answer(self, answer, entry):
        return _score_answer(answer, entry)
