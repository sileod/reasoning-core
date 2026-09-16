import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'counter_machine_trace (draw 1 of 3)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/counter_machine_trace',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
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

REGS = ['a', 'b', 'c', 'd', 'e', 'f']


@dataclass
class CounterMachineConfig(Config):
    num_regs: int = 2
    max_init: int = 3
    segments: int = 2
    max_steps: int = 200
    nest_chance: float = 0.15
    body_span: int = 3

    def apply_difficulty(self, level):
        self.num_regs = min(5, 2 + level // 2)
        self.max_init = 2 + level
        self.segments = 2 + level // 2
        self.max_steps = 150 + level * 80
        self.nest_chance = min(0.6, 0.15 + 0.08 * level)
        self.body_span = 2 + level


def _parse_int(s):
    return int(str(s).strip())


def _simulate(lines, init, trace_reg=None):
    vals = dict(init)
    n = len(lines)
    ip = 0
    steps = 0
    trace = [] if trace_reg is not None else None
    while ip < n:
        op, reg, target = lines[ip]
        if op == 'inc':
            vals[reg] += 1
            ip += 1
        elif op == 'dec':
            vals[reg] = max(0, vals[reg] - 1)
            ip += 1
        else:
            if vals[reg] == 0:
                if target == 'HALT':
                    ip = n
                else:
                    ip = target
            else:
                ip += 1
        steps += 1
        if trace is not None:
            trace.append(vals[trace_reg])
    return vals, steps, trace


def _gen_statements(num_regs, level_cfg):
    stmts = []
    regs = REGS[:num_regs]
    for _ in range(random.randint(1, level_cfg.body_span)):
        r = random.choice(regs)
        if random.random() < level_cfg.nest_chance:
            body = []
            others = [x for x in regs if x != r]
            for _ in range(random.randint(1, max(1, level_cfg.body_span - 1))):
                w = random.choice(others)
                body.append(('op', (random.choice(['inc', 'dec']), w)))
            stmts.append(('loop', r, body))
        else:
            op = random.choice(['inc', 'dec'])
            stmts.append(('op', (op, r)))
    return stmts


class CounterMachine:
    def __init__(self, cfg):
        self.cfg = cfg

    def build(self):
        num_regs = self.cfg.num_regs
        regs = REGS[:num_regs]
        init = {r: random.randint(0, self.cfg.max_init) for r in regs}
        prog = []
        used = set()
        for _ in range(self.cfg.segments):
            loop_reg = random.choice(regs)
            used.add(loop_reg)
            body = _gen_statements(num_regs, self.cfg)
            for s in body:
                if s[0] == 'op':
                    used.add(s[1][1])
                else:
                    for sub in s[2][1:]:
                        used.add(sub[1])
            prog.append(('loop', loop_reg, body))
        return init, prog, regs, used


def _linearize(prog):
    lines = []

    def stmt(s):
        if s[0] == 'op':
            op, reg = s[1]
            lines.append([op, reg, None])
        else:
            rt = s[1]
            start = len(lines)
            lines.append(['jz', rt, None])
            for inner in s[2]:
                stmt(inner)
            lines.append(['dec', rt, None])
            lines.append(['jz', rt, start])
            lines[start][2] = len(lines)

    for s in prog:
        stmt(s)
    for ln in lines:
        if ln[0] == 'jz' and ln[2] == len(lines):
            ln[2] = 'HALT'
    return lines


def _render(init, prog_lines):
    out = []
    n = len(prog_lines)
    for i, ln in enumerate(prog_lines, start=1):
        op, reg, target = ln
        if op == 'jz':
            if target == 'HALT':
                out.append(f"{i}: JZ {reg} END")
            else:
                out.append(f"{i}: JZ {reg} {target + 1}")
        else:
            out.append(f"{i}: {op.upper()} {reg}")
    return out


class CounterMachineTrace(Task):
    summary = ('Trace counter-machine programs where registers increment, decrement, and '
               'jump-if-zero through labeled lines; modes ask for a named register\'s value at '
               'halt, the total step count, or one register\'s value trace across the run.')
    design_choice = ('Instances present programs as plain text with labels and instructions; '
                     'solvers must parse the syntax before simulating, so difficulty lies in both '
                     'parsing and execution.')
    config_cls = CounterMachineConfig

    def generate_entry(self):
        cfg = self.config
        while True:
            builder = CounterMachine(cfg)
            init, prog, regs, used = builder.build()
            lines = _linearize(prog)
            if cfg.num_regs <= 2 and len(used) < 1:
                continue
            mode = random.choice(['value', 'steps', 'trace'])
            if mode in ('value', 'trace'):
                pool = [r for r in regs if r in used]
                if not pool:
                    pool = regs
                ask_reg = random.choice(pool)
            else:
                ask_reg = None
            final, steps, trace = _simulate(lines, init, ask_reg)
            if steps < 1 or steps > cfg.max_steps:
                continue
            if mode == 'value':
                answer = str(final[ask_reg])
            elif mode == 'steps':
                answer = str(steps)
            else:
                answer = ','.join(str(v) for v in trace)
            rendered = _render(init, lines)
            metadata = edict({
                'mode': mode,
                'regs': regs,
                'init': dict(init),
                'program': rendered,
                'ask_reg': ask_reg,
                '_final': dict(final),
                '_steps': steps,
            })
            metadata['_answer'] = answer
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        prog = '\n'.join(metadata.program)
        init_str = ', '.join(f"{r} = {metadata.init[r]}" for r in metadata.regs)
        if metadata.mode == 'value':
            q = f"What is the value of register {metadata.ask_reg} when the program halts?"
            ans = 'The answer is a single integer.'
        elif metadata.mode == 'steps':
            q = ('How many instructions are executed in total from the first line until the '
                 'program halts?')
            ans = 'The answer is a single integer.'
        else:
            q = (f"Give the value of register {metadata.ask_reg} after each executed instruction, "
                 f"in the order they execute. The first entry is its value after the first "
                 f"instruction, and so on.")
            ans = 'The answer is a comma-separated list of integers.'
        return (f"A counter machine has registers {', '.join(metadata.regs)} holding "
                f"non-negative integers, initially {init_str}. Its program is the following "
                f"labeled list of lines. On each line, INC r adds 1 to register r, DEC r subtracts "
                f"1 from register r (capped at 0), and 'JZ r L' jumps to the line labeled L when "
                f"register r is 0, otherwise it continues to the next line. Execution starts at "
                f"line 1 and runs one instruction at a time, continuing to the next line unless a "
                f"jump is taken; it halts when control passes beyond the last line (a 'JZ r END' "
                f"jump also halts).\n\nProgram:\n{prog}\n\n{q}\n{ans}")

    def score_answer(self, answer, entry):
        if entry.metadata.mode == 'trace':
            try:
                got = [_parse_int(x) for x in answer.split(',')]
            except (ValueError, TypeError):
                return 0.0
            try:
                exp = [_parse_int(x) for x in entry.answer.split(',')]
            except (ValueError, TypeError):
                return 0.0
            return 1.0 if got == exp else 0.0
        try:
            return 1.0 if _parse_int(answer) == _parse_int(entry.answer) else 0.0
        except (ValueError, TypeError):
            return 0.0
