import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'crdt_gossip_state_trace (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/crdt_gossip_state_trace',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _merge_gcounter(states):
    keys = sorted(set().union(*(s.keys() for s in states)))
    return {k: max(s.get(k, 0) for s in states) for k in keys}


def _merge_dict_sets(states, idx):
    keys = sorted(set().union(*(s.keys() for s in states)))
    out = {}
    for k in keys:
        s = set()
        for st in states:
            s |= set(st.get(k, [])[idx])
        out[k] = list(s)
    return out


def _read_value(ctype, state, rep):
    if ctype == 'gcounter':
        return state[rep]
    if ctype == 'pncounter':
        return state[rep][0] - state[rep][1]
    if ctype == 'lwwreg':
        return state[rep][1]
    return sorted(state[rep][0] - set(state[rep][1]))


def _snapshot(state):
    out = {}
    for k, v in state.items():
        if isinstance(v, list) and v and isinstance(v[0], list):
            out[k] = [list(x) for x in v]
        elif isinstance(v, list) and v and isinstance(v[0], set):
            out[k] = (set(v[0]), set(v[1]))
        else:
            out[k] = v
    return out


def _simulate(ctype, initial, ops):
    if ctype == 'gcounter':
        state = dict(initial)
        for op in ops:
            if op[0] == 'inc':
                for r, amt in op[1]:
                    state[r] = state.get(r, 0) + amt
            elif op[0] == 'merge':
                state = _merge_gcounter([state, op[1]])
        return state

    if ctype == 'pncounter':
        state = {k: list(v) for k, v in initial}
        for op in ops:
            if op[0] == 'inc':
                for r, amt in op[1]:
                    if amt > 0:
                        state[r][0] += amt
                    else:
                        state[r][1] += -amt
            elif op[0] == 'merge':
                ms = [state, op[1]]
                keys = sorted(set.union(*(set(s.keys()) for s in ms)))
                merged = {}
                for k in keys:
                    merged[k] = [max(ms[0].get(k, [0, 0])[0], ms[1].get(k, [0, 0])[0]),
                                 max(ms[0].get(k, [0, 0])[1], ms[1].get(k, [0, 0])[1])]
                state = merged
        return state

    if ctype == 'lwwreg':
        state = {k: (t, v) for k, (t, v) in initial}
        now = max((t for t, _ in state.values()), default=0)
        for op in ops:
            if op[0] == 'set':
                for r, val in op[1]:
                    now += 1
                    state[r] = (now, val)
            elif op[0] == 'merge':
                merged = dict(state)
                for k, (t, v) in op[1].items():
                    if k not in merged or t > merged[k][0]:
                        merged[k] = (t, v)
                state = merged
        return state

    # awset
    state = {k: (set(adds), set(dels)) for k, (adds, dels) in initial}
    for op in ops:
        if op[0] == 'add':
            for r, item in op[1]:
                if item not in state[r][1]:
                    state[r][0].add(item)
        elif op[0] == 'rm':
            for r, item in op[1]:
                state[r][1].add(item)
                state[r][0].discard(item)
        elif op[0] == 'merge':
            adds = _merge_dict_sets([state, op[1]], 0)
            dels = _merge_dict_sets([state, op[1]], 1)
            merged = {}
            for k in sorted(set.union(*(set(s.keys()) for s in [state, op[1]]))):
                merged[k] = (set(adds.get(k, [])), set(dels.get(k, [])))
            state = merged
    return state


@dataclass
class CRDTConfig(Config):
    level: int = 0
    n_replicas: int = 2
    n_local_ops: int = 1
    n_merges: int = 0

    def apply_difficulty(self, level):
        self.level = level
        self.n_replicas = 2 if level < 3 else 3
        self.n_local_ops = 1 + level
        self.n_merges = 0 if level < 2 else (1 if level < 5 else 2)


class CRDTGossipStateTrace(Task):
    summary = ("Generate a gossip CRDT trace across replicas: grow-only counters, PN "
               "counters, last-writer-wins registers, and add-wins sets that mutate locally "
               "and merge pairwise; ask a replica's value at a chosen stage or after "
               "convergence, answered as counter:N, pn:N, reg:val, or set:[a,b].")
    config_cls = CRDTConfig
    design_choice = ("Answer format: a single canonical string like 'counter:12' or "
                     "'set:[a,b]' or 'reg:val', chosen from a fixed vocabulary per type.")

    def generate_entry(self):
        for _ in range(200):
            entry = self._gen()
            if entry is not None and self._check(entry):
                return entry
        raise RuntimeError('failed to generate valid entry')

    def _gen(self):
        cfg = self.config
        n_rep = cfg.n_replicas
        replicas = list(range(n_rep))
        ctype = random.choice(['gcounter', 'pncounter', 'lwwreg', 'awset'])

        if ctype == 'gcounter':
            initial = [(r, random.randint(0, 3)) for r in replicas]
        elif ctype == 'pncounter':
            initial = [(r, [random.randint(0, 3), random.randint(0, 3)]) for r in replicas]
        elif ctype == 'lwwreg':
            initial = [(r, (random.randint(1, 3), random.randint(0, 9))) for r in replicas]
        else:
            initial = [(r, (random.sample(['a', 'b', 'c', 'd'], random.randint(0, 2)), []))
                       for r in replicas]

        ops = []
        for _ in range(cfg.n_local_ops):
            r = random.choice(replicas)
            if ctype == 'gcounter':
                ops.append(('inc', [(r, random.randint(1, 3))]))
            elif ctype == 'pncounter':
                a = random.randint(1, 3)
                if random.random() < 0.5:
                    a = -a
                ops.append(('inc', [(r, a)]))
            elif ctype == 'lwwreg':
                ops.append(('set', [(r, random.randint(0, 9))]))
            else:
                ops.append((random.choice(['add', 'rm']), [(r, random.choice(['a', 'b', 'c', 'd']))]))

        # insert merges interspersed
        final_ops = list(ops)
        nm = cfg.n_merges
        if nm:
            pos = random.sample(range(len(ops) + 1), nm)
            pos = sorted(pos, reverse=True)
            remote_states = []
            for _ in range(n_rep):
                if ctype == 'gcounter':
                    remote_states.append({r: random.randint(0, 3) for r in replicas})
                elif ctype == 'pncounter':
                    remote_states.append({r: [random.randint(0, 3), random.randint(0, 3)]
                                          for r in replicas})
                elif ctype == 'lwwreg':
                    remote_states.append({r: (random.randint(4, 10), random.randint(0, 9))
                                          for r in replicas})
                else:
                    remote_states.append({r: (random.sample(['a', 'b', 'c', 'd'], random.randint(0, 2)), [])
                                          for r in replicas})
            for p in pos:
                other = random.randrange(n_rep)
                final_ops.insert(p, ('merge', remote_states[other]))

        # query a specific replica after simulated state
        query_rep = random.choice(replicas)
        state = _simulate(ctype, initial, final_ops)
        val = _read_value(ctype, state, query_rep)

        if ctype == 'gcounter':
            answer = f"counter:{val}"
        elif ctype == 'pncounter':
            answer = f"pn:{val}"
        elif ctype == 'lwwreg':
            answer = f"reg:{val}"
        else:
            answer = 'set:[' + ','.join(val) + ']'

        metadata = {
            'ctype': ctype,
            'initial': initial,
            'ops': final_ops,
            'query_rep': query_rep,
            'answer': answer,
        }
        return Entry(metadata=metadata, answer=answer)

    def _check(self, entry):
        m = entry.metadata
        state = _simulate(m['ctype'], m['initial'], m['ops'])
        val = _read_value(m['ctype'], state, m['query_rep'])
        if m['ctype'] == 'gcounter':
            return f"counter:{val}" == m['answer']
        if m['ctype'] == 'pncounter':
            return f"pn:{val}" == m['answer']
        if m['ctype'] == 'lwwreg':
            return f"reg:{val}" == m['answer']
        return 'set:[' + ','.join(val) + ']' == m['answer']

    def render_prompt(self, metadata):
        ctype = metadata['ctype']
        init = metadata['initial']
        lines = []
        if ctype == 'gcounter':
            lines.append('We run a grow-only counter CRDT across replicas; a replica only counts upward and merges by taking the max contribution for every replica.')
            lines.append('Initial counts: ' + ', '.join(f'r{r}={v}' for r, v in init) + '.')
        elif ctype == 'pncounter':
            lines.append('We run a PN counter CRDT; each replica tracks a positive and negative count and the net is positive minus negative.')
            lines.append('Initial counts: ' + ', '.join(f'r{r}={{{v[0]},{v[1]}}}' for r, v in init) + '.')
        elif ctype == 'lwwreg':
            lines.append('We run a last-writer-wins register CRDT; each replica holds (timestamp, value) and the highest timestamp wins.')
            lines.append('Initial state: ' + ', '.join(f'r{r}=(ts{t},v{v})' for r, (t, v) in init) + '.')
        else:
            lines.append('We run an add-wins set CRDT; each replica holds a set and removes only tombstone the element.')
            lines.append('Initial sets: ' +
                         ', '.join(f'r{r}={{{",".join(sorted(a))}}}' if a else f'r{r}={{}}'
                                   for r, (a, _) in init) + '.')

        for op in metadata['ops']:
            kind = op[0]
            if kind == 'inc':
                lines.append(' '.join(f'r{r} increments by {a}.' for r, a in op[1]))
            elif kind == 'set':
                lines.append(' '.join(f'r{r} sets value to {v}.' for r, v in op[1]))
            elif kind == 'add':
                lines.append(' '.join(f'r{r} adds {i}.' for r, i in op[1]))
            elif kind == 'rm':
                lines.append(' '.join(f'r{r} removes {i}.' for r, i in op[1]))
            else:
                st = op[1]
                rep = metadata['query_rep']
                lines.append(f'r{rep} merges with another replica whose state is ' +
                             _render_remote(ctype, st) + '.')

        lines.append(f'After all operations, which value does replica r{metadata["query_rep"]} hold?')
        if ctype == 'gcounter':
            lines.append('Answer as counter:N (N is the counted value).')
        elif ctype == 'pncounter':
            lines.append('Answer as pn:N (N is the net value).')
        elif ctype == 'lwwreg':
            lines.append('Answer as reg:val.')
        else:
            lines.append('Answer as set:[a,b] (the surviving elements).')
        return '\n'.join(lines)

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0

    def distractor_candidates(self, entry):
        return []


def _render_remote(ctype, st):
    if ctype == 'gcounter':
        return '; '.join(f'r{r}={v}' for r, v in sorted(st.items()))
    if ctype == 'pncounter':
        return '; '.join(f'r{r}={{{v[0]},{v[1]}}}' for r, v in sorted(st.items()))
    if ctype == 'lwwreg':
        return '; '.join(f'r{r}=(ts{t},v{v})' for r, (t, v) in sorted(st.items()))
    return '; '.join(f'r{r}={{{",".join(sorted(a))}}}' if a else f'r{r}={{}}'
                     for r, (a, _) in sorted(st.items()))
