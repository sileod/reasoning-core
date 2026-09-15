import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

OFFSET = {"alu": 1, "ld": 2, "slow": 3}

ALU_OPS = ["add", "sub", "and", "or"]
SLOW_OPS = ["mul", "div"]

CONSUMER_READ_STAGE = 2  # EX stage index; consumer reads operands at cycle C_c + 2


def _schedule_formula(instrs):
    """Return (issue_cycles, total_stalls) by dependency-constrained scheduling."""
    n = len(instrs)
    C = [0] * n
    lastwrite = {}
    C[0] = 0
    lastwrite[instrs[0][0]] = (0, instrs[0][2])
    for k in range(1, n):
        dest, srcs, cls = instrs[k]
        req = C[k - 1] + 1
        for s in srcs:
            if s in lastwrite:
                p, pcls = lastwrite[s]
                req = max(req, C[p] + OFFSET[pcls])
        C[k] = req
        lastwrite[dest] = (k, cls)
    total = C[-1] - (n - 1)
    return C, total


def _schedule_cyclewise(instrs):
    """Independent cycle-by-cycle issue simulation; must agree with _schedule_formula."""
    n = len(instrs)
    avail = {}
    C = [None] * n
    k = 0
    t = 0
    while k < n:
        dest, srcs, cls = instrs[k]
        ok = True
        if k > 0 and t < C[k - 1] + 1:
            ok = False
        if ok:
            for s in srcs:
                if s in avail and avail[s] > t + CONSUMER_READ_STAGE:
                    ok = False
                    break
        if not ok:
            t += 1
            continue
        C[k] = t
        avail[dest] = t + CONSUMER_READ_STAGE + OFFSET[cls]
        k += 1
        t += 1
    total = C[-1] - (n - 1)
    return C, total


@dataclass
class PipelineHazardConfig(Config):
    count: int = 5
    regs: int = 4

    def apply_difficulty(self, level):
        self.count = 5 + 2 * level
        self.regs = 4 + (level // 3)


class PipelineHazardTraceTask(Task):
    task_name = "pipeline_hazard_trace"
    summary = ("Clock an in-order five-stage pipeline over instruction lists with register "
               "dependencies under stated alu/ld/slow forwarding rules, returning the total "
               "stall cycles as an integer.")
    design_choice = "Answer is the total stall cycles as an integer, with forwarding rules given textually and dependencies spread across all five stages."
    config_cls = PipelineHazardConfig

    def _gen_instr(self, cfg):
        roll = random.random()
        regs = list(range(cfg.regs))
        if roll < 0.45:
            op = random.choice(ALU_OPS)
            cls = "alu"
            dest = random.choice(regs)
            srcs = [random.choice(regs), random.choice(regs)]
        elif roll < 0.75:
            op = "ld"
            cls = "ld"
            dest = random.choice(regs)
            srcs = [random.choice(regs)]
        else:
            op = random.choice(SLOW_OPS)
            cls = "slow"
            dest = random.choice(regs)
            srcs = [random.choice(regs), random.choice(regs)]
        return (op, dest, srcs, cls)

    def generate_entry(self):
        cfg = self.config
        for _ in range(500):
            instrs = []
            for i in range(cfg.count):
                instrs.append(self._gen_instr(cfg))
            pairs = [(d, s, c) for (op, d, s, c) in instrs]
            C1, t1 = _schedule_formula(pairs)
            C2, t2 = _schedule_cyclewise(pairs)
            if C1 != C2 or t1 != t2:
                continue
            if t1 < 1:
                continue
            metadata = {
                "count": cfg.count,
                "regs": cfg.regs,
                "instructions": [
                    {"op": op, "dest": d, "sources": s, "class": c}
                    for (op, d, s, c) in instrs
                ],
                "issue": C1,
                "stall_cycles": int(t1),
            }
            return Entry(metadata=metadata, answer=str(int(t1)))
        raise RuntimeError("could not generate a valid pipeline trace")

    def render_prompt(self, metadata):
        lines = []
        for i, inst in enumerate(metadata["instructions"]):
            if inst["class"] == "alu":
                lines.append(f"i{i}: {inst['op']} r{inst['dest']} = r{inst['sources'][0]} r{inst['sources'][1]}")
            elif inst["class"] == "ld":
                lines.append(f"i{i}: ld r{inst['dest']} = mem[r{inst['sources'][0]}]")
            else:
                lines.append(f"i{i}: {inst['op']} r{inst['dest']} = r{inst['sources'][0]} r{inst['sources'][1]}")
        trace = "\n".join(lines)
        return (
            "An in-order single-issue pipelined processor with five stages "
            "(Fetch, Decode, Execute, Memory, Writeback) executes the instruction list below. "
            "Instructions issue in program order, one per cycle, unless a dependency forces a stall. "
            "Each instruction reads its source registers when it enters Execute. A result becomes "
            "usable for a dependent instruction's Execute stage according to its producing class:\n"
            "- alu (add/sub/and/or): usable one cycle after the producer's Execute stage;\n"
            "- ld: usable one cycle after the producer's Memory stage (load-use);\n"
            "- slow (mul/div): usable only at the producer's Writeback stage (no forwarding).\n"
            "When an instruction's needed operand is not yet usable, it is held (stalled) in Decode, "
            "inserting one stall cycle per extra cycle of waiting, and this delays every later "
            "instruction. Compute the total number of stall cycles inserted (the total bubbles; "
            "answer 0 if none).\n"
            "Instructions are given 0-indexed as i<index>: <op> r<dest> = <sources>.\n\n"
            + trace +
            "\n\nAnswer with a single integer: the total stall cycles."
        )

    def score_answer(self, answer, entry):
        try:
            gold = int(entry.answer)
            got = int(str(answer).strip())
        except (TypeError, ValueError):
            return 0.0
        return 1.0 if gold == got else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'pipeline_hazard_trace (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_verification_repair_r1/pipeline_hazard_trace',
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
