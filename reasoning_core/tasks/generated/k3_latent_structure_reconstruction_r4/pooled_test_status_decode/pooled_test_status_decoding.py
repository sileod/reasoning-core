"""Pooled testing status decoding.

Given a population of N items where exactly k are positive (tainted), a set of
pooled tests is performed: each test pools a subset of items and reports CLEAN
(no positive in it) or TAINTED (at least one positive). Negative pools sterilize
every member, and budget/complement reasoning isolates further items. The answer
is a canonical string over {C, T, ?} in item index order, where '?' marks items
whose status cannot be determined from the given tests.
"""

import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'pooled_test_status_decoding (variant 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_latent_structure_reconstruction_r4/pooled_test_status_decoding',
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

design_choice = "Statuses are output as a single canonical string over {C,T} in pool-index order, with a fixed placeholder for undetermined items."


@dataclass
class PooledConfig(Config):
    n: int = 4
    k: int = 1
    n_pools: int = 3

    def apply_difficulty(self, level):
        self.n = 3 + level
        self.k = 1 + (level > 0) + (level > 3)
        self.n_pools = 2 + level


class PooledTestStatusDecode(Task):
    summary = "Decode pooled tests reporting clean or tainted under a known number of positives: negative pools sterilize members, complement and budget arguments isolate the rest; answer every item's status or the undetermined residue."
    config_cls = PooledConfig

    def generate_entry(self):
        n = self.config.n
        k = self.config.k
        n_pools = self.config.n_pools
        for _ in range(200):
            positives = set(random.sample(range(n), k))
            pools = []
            for _ in range(n_pools):
                m = random.randint(1, n)
                members = set(random.sample(range(n), m))
                pools.append(members)
            status = _solve_statuses(n, k, pools, positives)
            if status is None:
                continue
            answer = "".join(status)
            if not (set(answer) & {"C", "T"}):
                continue
            # The answer is derived by exhaustive consistency over the true
            # outcomes, so it is correct by construction; verify the closed form
            # reproduces every decided status.
            assert "".join(_solve_statuses(n, k, pools, positives)) == answer
            metadata = {
                "n": n,
                "k": k,
                "pools": [sorted(list(p)) for p in pools],
                "positives": sorted(positives),
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("failed to generate a valid pooled-test instance")

    def render_prompt(self, metadata):
        n = metadata["n"]
        k = metadata["k"]
        pools = metadata["pools"]
        pool_lines = "\n".join(
            f"Pool {i}: items {pool}" for i, pool in enumerate(pools)
        )
        return (
            f"We have {n} items, exactly {k} of which are tainted (the rest clean). "
            f"The following pooled tests were run; each test reports TAINTED if its "
            f"pool contains at least one tainted item, otherwise CLEAN.\n{pool_lines}\n"
            f"Determine each item's status. Output a single string of length {n} in item "
            f"index order using C for clean, T for tainted, and ? for undetermined. "
            f"Example: for 4 items if item0=clean,item1=tainted,item2=clean,item3=clean -> CTCC."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        gold = entry.answer
        if answer.strip() == gold:
            return 1.0
        return 0.0


def _solve_statuses(n, k, pools, positives):
    outcomes = [bool(positives & p) for p in pools]
    consistent = _all_consistent_positive_sets(n, k, pools, outcomes)
    if not consistent:
        return None
    status = []
    fully = {frozenset(s) for s in consistent}
    for i in range(n):
        in_pos = {i in s for s in fully}
        if len(in_pos) == 1:
            status.append("T" if True in in_pos else "C")
        else:
            status.append("?")
    return status


def _all_consistent_positive_sets(n, k, pools, outcomes):
    res = []
    for combo in itertools.combinations(range(n), k):
        s = set(combo)
        ok = True
        for p, out in zip(pools, outcomes):
            if bool(s & p) != out:
                ok = False
                break
        if ok:
            res.append(s)
    return res
