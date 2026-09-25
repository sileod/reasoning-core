"""Abacus partition transfer: beta sets <-> cores and quotients.

Translate a labelled beta set across r runners into its r-core beta set and
the r runner-quotient beta sets, tracking each bead's origin by a unique ID.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'abacus_partition_transfer (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r5/abacus_partition_transfer',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class AbacusPartitionTransferConfig(Config):
    n: int = 5
    r: int = 2
    max_pos: int = 12

    def apply_difficulty(self, level):
        self.r = min(4, 2 + level // 3)
        self.n = 4 + min(6, level)
        self.max_pos = 12 + 4 * level


def _compute(beta, r):
    """Return (core, quotient, origins) for a beta set across r runners.

    Each bead is labelled by its (distinct) starting position.  Sliding every
    bead up on its own runner pushes a bead whose row has rank k (among that
    runner's rows, ascending) to core row k, so its core position is
    j + r*k.  The quotient beta set of runner j is the sorted original rows of
    that runner's beads (the standard beta-set encoding of the quotient).
    """
    beta = sorted(beta)
    rows = [[] for _ in range(r)]
    for p in beta:
        rows[p % r].append(p // r)
    for j in range(r):
        rows[j].sort()

    quotient = [list(rows[j]) for j in range(r)]

    core = []
    for j in range(r):
        m = len(rows[j])
        for k in range(m):
            core.append(j + r * k)
    core = sorted(core)

    # origins: for each bead (label == starting position) its core position.
    origins = []
    for p in beta:
        j = p % r
        h = p // r
        rank = rows[j].index(h)
        origins.append((p, j + r * rank))
    origins.sort()

    # Reconstruction check: from the core rows and the quotient rows, rebuild
    # the original beta set and require it to match.
    rebuilt = []
    for j in range(r):
        for k, orig_h in enumerate(quotient[j]):
            rebuilt.append(j + r * orig_h)
    rebuilt.sort()
    if rebuilt != beta:
        raise RuntimeError("core/quotient recombination failed")
    return core, quotient, origins


class AbacusPartitionTransfer(Task):
    summary = ("Translate labelled beta sets across 2-4 runners into r-core beta sets and "
               "runner-quotient beta sets, tracking bead origins by unique IDs before sliding.")
    design_choice = ("Present a beta set with a specified number of runners; ask for the core and "
                     "the quotient as a list of beta sets, with bead origins tracked by labeling "
                     "beads with unique IDs before sliding.")
    task_version = 2
    config_cls = AbacusPartitionTransferConfig

    def generate_entry(self):
        cfg = self.config
        beta = random.sample(range(0, cfg.max_pos + 1), cfg.n)
        core, quotient, origins = _compute(beta, cfg.r)

        core_str = ",".join(str(x) for x in core)
        quot_str = ";".join(",".join(str(x) for x in q) if q else "0" for q in quotient)
        orig_str = ",".join(f"{a}->{b}" for a, b in origins)
        answer = f"core={core_str};quot={quot_str};orig={orig_str}"

        metadata = {
            "beta": sorted(beta),
            "r": cfg.r,
            "core": core,
            "quotient": quotient,
            "origins": origins,
            "answer": answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        beta = metadata["beta"]
        r = metadata["r"]
        beads = ", ".join(f"{p}" for p in beta)
        runners = {}
        for p in beta:
            runners.setdefault(p % r, []).append(p)
        runner_lines = []
        for j in range(r):
            ps = runners.get(j, [])
            runner_lines.append(
                f"runner {j}: " + (", ".join(str(p) for p in sorted(ps)) or "empty"))
        prompt = (
            f"A beta set of {len(beta)} distinct bead positions "
            f"({beads}) is placed on an abacus with {r} runners, one runner per "
            f"residue class mod {r}: a bead at position p sits on runner p mod r "
            "at row floor(p/r). Each bead is labelled by its starting position. "
            "Slide every bead up on its own runner as far as it can go (row by "
            "row) to form the r-core; the quotient records, for each runner, the "
            "original rows of that runner's beads (a list of runner beta sets). "
            "The core beta set is the set of bead positions after sliding. "
            "Report the r-core beta set, the quotient as a list of runner beta "
            "sets, and every bead's core position, as:\n"
            "core=<core positions, ascending, comma-separated>;"
            "quot=<q0>;<q1>;...;<q(r-1)> (each qj = that runner's original rows, "
            "ascending comma-separated, 0 if the runner is empty);"
            "orig=<label->corepos, for each label ascending, comma-separated>.\n"
            "Runners:\n"
            + "\n".join(runner_lines)
        )
        return prompt

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == str(entry.answer).strip() else 0.0
