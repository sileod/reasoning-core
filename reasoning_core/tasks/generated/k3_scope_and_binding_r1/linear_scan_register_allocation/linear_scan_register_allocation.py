import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class LinearScanRegisterAllocationConfig(Config):
    n_vars: int = 5
    n_uses: int = 8
    regs: int = 2
    max_pos: int = 20

    def apply_difficulty(self, level):
        self.n_vars = 4 + (level // 2)
        self.n_uses = 6 + 2 * level
        self.regs = 1 + (level // 4)
        self.max_pos = 15 + 4 * level


def _allocate(intervals, regs):
    """Linear-scan allocation on sparse integer-coordinate intervals.

    intervals: list of (start, end) live intervals, one per variable.
    Returns list of outcomes: an int register id or 'S' for spill.

    Process positions in increasing order: on a variable's start, first free the
    registers of intervals that already ended (end < start); if a register is free,
    assign the variable's start to it; else evict the currently-live variable with
    the farthest end and spill it. An interval evicted once stays spilled. A variable
    that would evict a variable with a farther end instead spills itself.
    """
    n = len(intervals)
    order = sorted(range(n), key=lambda i: intervals[i][0])
    outcomes = [None] * n
    holder = {}  # reg -> var index
    spilled = set()

    for i in order:
        s, e = intervals[i]
        for r in list(holder):
            var = holder[r]
            if intervals[var][1] < s:
                holder.pop(r, None)
        free = [r for r in range(regs) if r not in holder]
        if free:
            reg = free[0]
            holder[reg] = i
            outcomes[i] = reg
        else:
            active = [var for var in holder.values() if var is not None]
            victim = max(active, key=lambda var: intervals[var][1])
            if intervals[victim][1] > e:
                spilled.add(victim)
                reg = [r for r, var in holder.items() if var == victim][0]
                holder[reg] = i
                outcomes[i] = reg
            else:
                spilled.add(i)
                outcomes[i] = 'S'
    for i in range(n):
        if i in spilled:
            outcomes[i] = 'S'
    return outcomes


class LinearScanRegisterAllocation(Task):
    summary = ("Build live intervals from a def/use listing in one basic block, then run "
               "linear-scan allocation under a fixed register count: expire finished "
               "intervals, evict the farthest-ending one under pressure; answer each "
               "variable's register-or-spill outcome.")
    design_choice = ("Represent each variable's def/use positions as sparse integer "
                     "coordinates in a single basic block, with the answer formatted as "
                     "a compact sequence of register numbers or 'S' for spill.")
    config_cls = LinearScanRegisterAllocationConfig

    def generate_entry(self):
        cfg = self.config
        n = cfg.n_vars
        regs = cfg.regs
        max_pos = cfg.max_pos
        total_positions = max_pos + 1

        while True:
            assignments = []
            used = set()
            coord_pool = list(range(total_positions))
            random.shuffle(coord_pool)
            ok = True
            ci = 0
            for i in range(n):
                need = 2 + random.choice([0, 1, 1, 2])
                if ci + need > len(coord_pool):
                    ok = False
                    break
                coords = sorted(coord_pool[ci: ci + need])
                ci += need
                defc = coords[0]
                uses = coords[1:]
                assignments.append((defc, uses))
            if not ok:
                continue
            break

        intervals = [(defc, max([defc] + uses)) for defc, uses in assignments]
        outcomes = _allocate(intervals, regs)

        listing = []
        for i, (defc, uses) in enumerate(assignments):
            listing.append((i, 'def', defc))
            for u in uses:
                listing.append((i, 'use', u))
        listing.sort(key=lambda x: x[2])

        answer = '_'.join(str(o) for o in outcomes)
        metadata = {
            "n_vars": n,
            "regs": regs,
            "intervals": [[int(s), int(e)] for s, e in intervals],
            "listing": listing,
            "outcomes": outcomes,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append(f"A single basic block defines and uses {metadata['n_vars']} variables "
                     f"at integer positions. Registers available: {metadata['regs']}.")
        lines.append("Lines list 'variable op position'. A def starts a variable's live "
                     "interval; its live range ends at its last use.")
        for var, op, pos in metadata['listing']:
            lines.append(f"v{var} {op} at {pos}")
        lines.append("Run linear-scan allocation: process positions in increasing order; "
                     "on a variable's start first free the registers of intervals that "
                     "already ended (their end < current position); if a register is free "
                     "assign the variable's start to it, else evict the currently-live "
                     "variable whose end is farthest and spill it (an interval evicted once "
                     "stays spilled). A variable that would evict a variable with a farther "
                     "end instead spills itself.")
        lines.append("For each v0..vN-1 give the register it was assigned at its start, or "
                     "'S' for spilled, joined by underscores. Example: '0_S_1_0'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        outcomes = entry.metadata['outcomes']
        expected = '_'.join(str(o) for o in outcomes)
        return 1.0 if answer == expected else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'linear_scan_register_allocation (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/linear_scan_register_allocation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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
