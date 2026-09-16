import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'event_driven_gate_simulation (draw 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_semantics_r1/event_driven_gate_simulation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

GATE_FUNCS = {
    'AND': lambda vs: int(all(vs)),
    'NAND': lambda vs: int(not all(vs)),
    'OR': lambda vs: int(any(vs)),
    'NOR': lambda vs: int(not any(vs)),
    'XOR': lambda vs: int(sum(vs) % 2),
    'XNOR': lambda vs: int(1 - (sum(vs) % 2)),
    'NOT': lambda vs: int(not vs[0]),
    'BUF': lambda vs: int(vs[0]),
}

ONE_IN = {'NOT', 'BUF'}


def value_at(wave, t):
    if not wave:
        return 0
    v = wave[0][1]
    for (wt, wv) in wave:
        if wt <= t:
            v = wv
        else:
            break
    return v


def combine(func, waves):
    times = set()
    for w in waves:
        for (t, _v) in w:
            times.add(t)
    times = sorted(times)
    res = []
    prev = None
    for t in times:
        vals = [value_at(w, t) for w in waves]
        out = func(vals)
        if out != prev:
            res.append((t, out))
            prev = out
    return res


def shift(wave, d):
    return [(t + d, v) for (t, v) in wave]


def normalize(w):
    w = [tuple(x) for x in w]
    if not w:
        return [(0, 0)]
    if w[0][0] > 0:
        w = [(0, w[0][1])] + w
    out = []
    pt = None
    for (t, v) in w:
        if pt is not None and (t == pt[0] or v == pt[1]):
            continue
        out.append((t, v))
        pt = (t, v)
    return out


def to_runs(wave, horizon):
    runs = []
    for idx, (t, v) in enumerate(wave):
        end = wave[idx + 1][0] if idx + 1 < len(wave) else horizon
        if end - t > 0:
            runs.append((t, end, v))
    return runs


def filt_wave(wave, d, horizon):
    runs = to_runs(wave, horizon)
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(runs):
            s, e, v = runs[i]
            if (e - s) < d:
                if i > 0 and i + 1 < len(runs) and runs[i - 1][2] == runs[i + 1][2]:
                    nb, ne, nv = runs[i - 1]
                    runs[i - 1] = (nb, runs[i + 1][1], nv)
                    del runs[i + 1]
                    changed = True
                    continue
                else:
                    del runs[i]
                    changed = True
                    continue
            i += 1
    out = []
    for (s, _e, v) in runs:
        if not out or out[-1][1] != v:
            out.append((s, v))
    return out


def node_wave(input_waves, gates, out_node):
    """Transport/inertial waveforms keyed by node name (topological since gates are ordered)."""
    node_waves = {k: normalize(w) for (k, w) in input_waves.items()}
    for g in gates:
        ins = [node_waves[p] for p in g['inputs']]
        z = combine(GATE_FUNCS[g['type']], ins)
        hor = _horizon(node_waves)
        delayed = normalize(shift(z, g['delay']))
        if g['mode'] == 'inertial':
            node_waves[g['name']] = normalize(filt_wave(delayed, g['delay'], hor))
        else:
            node_waves[g['name']] = delayed
    return node_waves


def _horizon(node_waves):
    m = 1
    for w in node_waves.values():
        for (t, _v) in w:
            m = max(m, t)
    return m + 4


def glitches(wave, dout, horizon):
    res = []
    for (s, e, _v) in to_runs(wave, horizon):
        if (e - s) < dout:
            res.append([s, e])
    return res


def fmt_transitions(wave):
    return ','.join('%d@%d' % (v, t) for (t, v) in wave)


def fmt_glitches(glist):
    if not glist:
        return '[]'
    return ','.join('[%d,%d]' % (a, b) for (a, b) in glist)


@dataclass
class EventDrivenGateSimulationV2Config(Config):
    n_gates: int = 2
    max_delay: int = 1
    max_trans: int = 2
    max_in: int = 1

    def apply_difficulty(self, level):
        self.n_gates = 2 + 2 * level
        self.max_delay = 1 + level
        self.max_trans = 2 + level
        self.max_in = 1 if level < 1 else (2 if level < 4 else 3)


class EventDrivenGateSimulation(Task):
    summary = ("Event-simulate a gate netlist with input waveforms and per-gate transport or "
               "inertial delays: combine zero-delay logic, shift by delay, cancel stale pulses "
               "narrower than the delay; vary fanout and reconvergent paths across AND/OR/NAND/"
               "NOR/XOR/XNOR/NOT; answer the timed output waveform and narrow-pulse glitch list.")
    design_choice = ("Encode the output waveform as a compact string of transitions (e.g., "
                     "'0@0,1@3,0@5') and separately list glitch intervals as [start,end] pairs "
                     "in chronological order.")
    task_version = 2
    config_cls = EventDrivenGateSimulationV2Config

    def generate_entry(self):
        cfg = self.config
        while True:
            meta = self._build_instance(cfg)
            gold = self._golds(meta)
            try:
                self._verify(meta, gold)
            except AssertionError:
                continue
            return Entry(metadata=meta, answer=gold)

    def _build_instance(self, cfg):
        n_in = random.randint(1, cfg.max_in)
        gates = []
        input_waves = {}
        horizon_target = n_in + cfg.n_gates + cfg.max_delay * 2 + 4
        for k in range(n_in):
            init = random.randint(0, 1)
            ntr = random.randint(1, cfg.max_trans)
            times = random.sample(range(1, max(2, horizon_target - 1)), ntr)
            times = sorted(times)
            wave = [(0, init)]
            v = init
            for t in times:
                v = 1 - v
                wave.append((t, v))
            input_waves['i%d' % k] = wave

        avail = list(input_waves.keys())
        type_pool = ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'XNOR']
        for j in range(cfg.n_gates):
            reconverge = (random.random() < 0.35 and j >= 1 and len(avail) >= 2)
            if reconverge:
                par1 = avail[-1]
                par2 = random.choice(gates[j - 1]['inputs'])
                if par2 == par1:
                    par2 = avail[random.randrange(len(avail) - 1)]
                parents = [par1, par2]
                gtype = random.choice(type_pool)
            else:
                if random.random() < 0.25:
                    gtype = 'NOT'
                else:
                    gtype = random.choice(type_pool)
                if gtype in ONE_IN:
                    parents = [random.choice(avail)]
                else:
                    k = random.randint(2, 3)
                    k = min(k, len(avail))
                    parents = random.sample(avail, k)
            d = random.randint(1, cfg.max_delay)
            mode = 'transport' if random.random() < 0.62 else 'inertial'
            name = 'g%d' % j
            gates.append({'name': name, 'type': gtype, 'inputs': parents,
                          'delay': d, 'mode': mode})
            avail.append(name)

        out_name = gates[-1]['name']
        gates[-1]['mode'] = 'transport'
        return {'inputs': [[k, input_waves[k]] for k in input_waves],
                'gates': gates, 'output': out_name}

    def _golds(self, meta):
        input_waves = {k: [tuple(x) for x in w] for (k, w) in meta['inputs']}
        gates = [dict(g, inputs=list(g['inputs'])) for g in meta['gates']]
        node_waves = self_compute(input_waves, gates)
        out_name = meta['output']
        outp = node_waves[out_name]
        out_gate = [g for g in gates if g['name'] == out_name][0]
        dout = out_gate['delay']
        hor = _horizon(node_waves)
        gl = glitches(outp, dout, hor)
        return fmt_transitions(outp) + '; ' + fmt_glitches(gl)

    def _verify(self, meta, gold):
        input_waves = {k: [tuple(x) for x in w] for (k, w) in meta['inputs']}
        gates = [dict(g, inputs=list(g['inputs'])) for g in meta['gates']]
        recomputed = self_compute(dict(input_waves), gates)
        out_name = meta['output']
        outp = recomputed[out_name]
        gold_wave = parse_wave(gold.split(';')[0])
        gold_gl = parse_glitches(gold.split(';')[1])
        assert gold_wave == outp, 'gold waveform mismatch'
        vals = [v for (_t, v) in gold_wave]
        assert all(x != y for x, y in zip(vals, vals[1:])), 'not alternating'
        times = [t for (t, _) in gold_wave]
        assert times == sorted(times) and len(set(times)) == len(times), 'times not strict'
        assert gold_wave[0][0] == 0 and gold_wave[0][1] in (0, 1), 'waveform must start at 0'
        out_gate = [g for g in gates if g['name'] == out_name][0]
        dout = out_gate['delay']
        hor = _horizon(recomputed)
        gl = glitches(outp, dout, hor)
        assert gl == gold_gl, 'glitch mismatch'
        for (a, b) in gl:
            assert 0 <= a < b, 'glitch bounds'
        if gl:
            prev_end = -1
            for (a, b) in gl:
                assert a >= prev_end, 'glitches not chronological'
                prev_end = b
        return True

    def render_prompt(self, metadata):
        return render_prompt_from(metadata)

    def score_answer(self, answer, entry):
        return 1.0 if _cmp_answer(answer, entry.answer) else 0.0

    def distractor_candidates(self, entry):
        return ()


def self_compute(input_waves, gates):
    node_waves = {k: normalize(tuple(x) for x in w) for (k, w) in input_waves.items()}
    for g in gates:
        ins = [node_waves[p] for p in g['inputs']]
        z = combine(GATE_FUNCS[g['type']], ins)
        hor = _horizon(node_waves)
        delayed = normalize(shift(z, g['delay']))
        if g['mode'] == 'inertial':
            node_waves[g['name']] = normalize(filt_wave(delayed, g['delay'], hor))
        else:
            node_waves[g['name']] = delayed
    return node_waves


def parse_wave(s):
    out = []
    for tok in s.strip().replace(' ', '').split(','):
        if not tok:
            continue
        v, t = tok.split('@')
        out.append((int(t), int(v)))
    return out


def parse_glitches(s):
    s = s.strip()
    if s == '[]' or s == '':
        return []
    s = s.strip('[]')
    out = []
    for tok in s.split('],'):
        tok = tok.strip('[]')
        a, b = tok.split(',')
        out.append([int(a), int(b)])
    return out


def _cmp_answer(answer, ref):
    try:
        if ';' not in answer or ';' not in ref:
            return False
        aw = parse_wave(answer.split(';')[0])
        rw = parse_wave(ref.split(';')[0])
        ag = parse_glitches(answer.split(';')[1])
        rg = parse_glitches(ref.split(';')[1])
        return aw == rw and ag == rg
    except Exception:
        return False


def _check_answer(answer):
    """Parse and validate an answer string structurally; returns lists or raises."""
    if ';' not in answer:
        raise ValueError('missing glitch section')
    w = parse_wave(answer.split(';')[0])
    g = parse_glitches(answer.split(';')[1])
    if not w or w[0][0] != 0:
        raise ValueError('waveform must start at 0')
    ts = [t for (t, _v) in w]
    if ts != sorted(ts) or len(set(ts)) != len(ts):
        raise ValueError('times not strictly increasing')
    return w, g


def render_prompt_from(meta):
    lines = []
    lines.append('A combinational netlist of digital gates is simulated as an event-driven system '
                 'over integer time, starting at t=0. Every node holds a boolean value; the only '
                 'given inputs are the input waveforms below. At t=0 every node already has its '
                 'steady-state value from the initial levels.')
    lines.append('Input waveforms (value@time transitions; held until the next one):')
    for (k, w) in meta['inputs']:
        lines.append('  %s: %s' % (k, fmt_transitions([tuple(x) for x in w])))
    lines.append('Gates (inputs, then delay, then mode). Modes: "transport" passes every pulse '
                 'through unchanged (just shifted by the gate delay); "inertial" cancels any '
                 'output pulse narrower than the gate delay, so such pulses never appear on '
                 'that gate\'s output (stale pulses are dropped).')
    for g in meta['gates']:
        lines.append('  %s = %s(%s) delay %d, %s' % (
            g['name'], g['type'], ','.join(g['inputs']), g['delay'], g['mode']))
    lines.append('The netlist is fanout-free to a single final output node: %s.' % meta['output'])
    lines.append('A glitch interval [a,b] is a maximal pulse on the final output whose width '
                 '(b-a) is strictly less than the delay of the final output gate; list glitches '
                 'in chronological order as [a,b] pairs, or [] if there are none.')
    lines.append('Answer on one line as the final output waveform "v@t,..." with the initial '
                 'value first at t=0, then ";", then the glitch list. Example: '
                 '"0@0,1@3,0@5,1@7; [3,5]".')
    return '\n'.join(lines)
