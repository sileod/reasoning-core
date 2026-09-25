import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'boolean_circuit_fault_diagnosis (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_reusable_operations_r4/boolean_circuit_fault_diagnosis',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _apply(op, vals):
    if op == 'AND':
        return int(vals[0] and vals[1])
    if op == 'OR':
        return int(vals[0] or vals[1])
    if op == 'NAND':
        return int(not (vals[0] and vals[1]))
    if op == 'NOR':
        return int(not (vals[0] or vals[1]))
    if op == 'XOR':
        return vals[0] ^ vals[1]
    if op == 'XNOR':
        return 1 - (vals[0] ^ vals[1])
    if op == 'NOT':
        return 1 - vals[0]
    raise ValueError(op)


def _sim(n_inputs, gate_ops, gate_ins, inputs, faults):
    val = list(inputs)
    fmap = dict(faults)
    for g in range(len(gate_ops)):
        node = n_inputs + g
        if node in fmap:
            val.append(fmap[node])
        else:
            val.append(_apply(gate_ops[g], [val[i] for i in gate_ins[g]]))
    return val


def _feeds_output(n_inputs, gate_ins, outputs):
    reach = set(outputs)
    changed = True
    while changed:
        changed = False
        for g in range(len(gate_ins)):
            node = n_inputs + g
            if node in reach:
                for iv in gate_ins[g]:
                    if iv not in reach:
                        reach.add(iv)
                        changed = True
    return reach


def _build_circuit(n_inputs, n_gates, n_out):
    inputs = [random.randint(0, 1) for _ in range(n_inputs)]
    twoin = ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR']
    gate_ops = []
    gate_ins = []
    for g in range(n_gates):
        node = n_inputs + g
        available = list(range(node))
        if random.random() < 0.15 and node >= n_inputs:
            gate_ops.append('NOT')
            gate_ins.append([random.choice(available)])
        else:
            a = random.choice(available)
            b = random.choice(available)
            tries = 0
            while b == a and len(available) > 1 and tries < 6:
                b = random.choice(available)
                tries += 1
            gate_ops.append(random.choice(twoin))
            gate_ins.append([a, b])
    outputs = list(range(n_inputs + n_gates - n_out, n_inputs + n_gates))
    return gate_ops, gate_ins, inputs, outputs


def _reproduces(n_inputs, gate_ops, gate_ins, inputs, outputs, observed, subset):
    for assign in itertools.product([0, 1], repeat=len(subset)):
        faults = sorted(zip(subset, assign))
        val = _sim(n_inputs, gate_ops, gate_ins, inputs, faults)
        if all(val[o] == observed[i] for i, o in enumerate(outputs)):
            return True
    return False


def _unique_min_diagnosis(n_inputs, gate_ops, gate_ins, inputs, outputs, observed, max_size, candidates):
    for d in range(0, max_size + 1):
        found = None
        for subset in itertools.combinations(candidates, d):
            if _reproduces(n_inputs, gate_ops, gate_ins, inputs, outputs, observed, subset):
                if found is not None:
                    return None
                found = subset
        if found is not None:
            return list(found)
    return None


@dataclass
class BCFDConfig(Config):
    n_inputs: int = 3
    n_gates: int = 6
    n_out: int = 1
    max_faults: int = 1
    mode_mix_detect: float = 0.5

    def apply_difficulty(self, level):
        self.n_inputs = 3
        self.n_gates = 6 + 2 * level
        self.n_out = 2 + (1 if level >= 4 else 0)
        mf = 2 + level // 2
        self.max_faults = min(mf, 3)


def _expected(n_inputs, gate_ops, gate_ins, inputs, outputs):
    val = _sim(n_inputs, gate_ops, gate_ins, inputs, [])
    return [val[o] for o in outputs]


class BooleanCircuitFaultDiagnosis(Task):
    summary = ("Diagnose single and multiple stuck-at faults in combinational "
               "circuits by propagating values and comparing observed outputs; "
               "answers are the set of faulty gates, a minimal diagnosis, or "
               "whether a fault is detectable.")
    config_cls = BCFDConfig
    task_version = 2
    _max_retries = 120

    def _gen_diag(self):
        cfg = self.config
        for _ in range(self._max_retries):
            gate_ops, gate_ins, inputs, outputs = _build_circuit(
                cfg.n_inputs, cfg.n_gates, cfg.n_out)
            cone = _feeds_output(cfg.n_inputs, gate_ins, outputs)
            out_set = set(outputs)
            candidates = sorted(n for n in cone if n >= cfg.n_inputs and n not in out_set)
            if len(candidates) < 1:
                continue
            k = random.randint(1, min(cfg.max_faults, len(candidates)))
            F = sorted(random.sample(candidates, k))
            faults = sorted((g, random.randint(0, 1)) for g in F)
            val = _sim(cfg.n_inputs, gate_ops, gate_ins, inputs, faults)
            observed = [val[o] for o in outputs]
            expected = _expected(cfg.n_inputs, gate_ops, gate_ins, inputs, outputs)
            diag = _unique_min_diagnosis(
                cfg.n_inputs, gate_ops, gate_ins, inputs, outputs, observed, k, candidates)
            if diag is not None and diag == F:
                metadata = {
                    'mode': 'diag',
                    'gate_ops': gate_ops,
                    'gate_ins': gate_ins,
                    'inputs': inputs,
                    'outputs': outputs,
                    'expected': expected,
                    'observed': observed,
                    'faulty': F,
                    'faults': [[g, s] for g, s in faults],
                }
                return Entry(metadata=metadata, answer=' '.join(str(g) for g in F))
        return None

    def _gen_detect(self):
        cfg = self.config
        target = 'detectable' if random.random() < 0.5 else 'undetectable'
        for _ in range(self._max_retries):
            gate_ops, gate_ins, inputs, outputs = _build_circuit(
                cfg.n_inputs, cfg.n_gates, cfg.n_out)
            cone = _feeds_output(cfg.n_inputs, gate_ins, outputs)
            internal = list(range(cfg.n_inputs, cfg.n_inputs + cfg.n_gates))
            if target == 'undetectable':
                gate = random.choice(internal)
                fault_free_val = _sim(cfg.n_inputs, gate_ops, gate_ins, inputs, [])[gate]
                stuck = fault_free_val
            else:
                cone_gates = sorted(n for n in cone if n >= cfg.n_inputs)
                if not cone_gates:
                    continue
                gate = random.choice(cone_gates)
                stuck = random.randint(0, 1)
            faults = [(gate, stuck)]
            val = _sim(cfg.n_inputs, gate_ops, gate_ins, inputs, faults)
            observed = [val[o] for o in outputs]
            expected = _expected(cfg.n_inputs, gate_ops, gate_ins, inputs, outputs)
            detectable = observed != expected
            if (target == 'detectable' and not detectable) or (target == 'undetectable' and detectable):
                continue
            metadata = {
                'mode': 'detect',
                'gate_ops': gate_ops,
                'gate_ins': gate_ins,
                'inputs': inputs,
                'outputs': outputs,
                'expected': expected,
                'observed': observed,
                'fault': [gate, stuck],
            }
            ans = 'YES' if detectable else 'NO'
            return Entry(metadata=metadata, answer=ans)
        return None

    def generate_entry(self):
        for _ in range(30):
            mode = 'detect' if random.random() < self.config.mode_mix_detect else 'diag'
            if mode == 'diag':
                ex = self._gen_diag()
            else:
                ex = self._gen_detect()
            if ex is not None:
                return ex
        raise RuntimeError("boolean_circuit_fault_diagnosis failed to generate")

    def render_prompt(self, metadata):
        m = metadata
        gate_lines = []
        for g in range(len(m['gate_ops'])):
            node = len(m['inputs']) + g
            ins = ', '.join('I%s' % i if i < len(m['inputs']) else 'g%s' % i for i in m['gate_ins'][g])
            gate_lines.append('g%s = %s(%s)' % (node, m['gate_ops'][g], ins))
        inp = ', '.join('I%s=%d' % (i, v) for i, v in enumerate(m['inputs']))
        exp = ', '.join('O%s=%d' % (i, v) for i, v in enumerate(m['expected']))
        if m['mode'] == 'diag':
            obs = ', '.join('O%s=%d' % (i, v) for i, v in enumerate(m['observed']))
            return ('A combinational circuit with primary inputs (I) and internal gates '
                    '(g) is given below; its primary outputs are O. Each internal gate '
                    'may be stuck-at-faulty, forcing its output to a fixed value. When a '
                    'set of internal gates is faulty the observed outputs differ from the '
                    'fault-free expected outputs. (The primary outputs are observation '
                    'pins, never faulty gates themselves.)\n\n%s\n\n%s\n\nExpected '
                    'outputs: %s\nObserved outputs: %s\n\nWhich internal gates are '
                    'stuck-at-faulty, i.e. the minimal set of internal gates whose stuck '
                    'values fully explain the observed outputs? Answer as the '
                    'space-separated gate indices in ascending order.'
                    % ('\n'.join(gate_lines), inp, exp, obs))
        fault = m['fault']
        return ('A combinational circuit with primary inputs is given below. A single '
                'gate is stuck-at-faulty: its output is forced to a fixed value.\n\n'
                '%s\n\n%s\n\nFault: g%d is stuck-at %d\nFault-free expected outputs: %s\n\n'
                'Is this fault detectable, i.e. does it change at least one observed '
                'output compared to the fault-free circuit? Answer with YES or NO as '
                'the only content.'
                % ('\n'.join(gate_lines), inp, fault[0], fault[1], exp))

    def score_answer(self, answer, entry):
        mode = entry.metadata.mode
        ref = str(entry.answer).strip()
        ans = str(answer).strip()
        if mode == 'detect':
            return 1.0 if ans.upper() == ref.upper() else 0.0
        try:
            a = sorted(int(x) for x in ans.split())
            r = sorted(int(x) for x in ref.split())
        except (ValueError, TypeError):
            return 0.0
        return 1.0 if a == r else 0.0
