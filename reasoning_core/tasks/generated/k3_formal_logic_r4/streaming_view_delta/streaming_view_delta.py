import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'streaming_view_delta (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_logic_r4/streaming_view_delta',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

design_choice = "Answer form: emit per-tuple delta strings like '+k,v' or '-k,v' for every changed aggregate, versus a single corrected row for a queried key."


def _simulate(events, b_keys, cond_key=None):
    """Run the bag-join view over a base relation B with given keys.

    Each A tuple (tid, key, qty, attr) counts qty toward key's sum iff key in
    B (antijoin else) and, if cond_key is set, iff attr == cond_key
    (conditional grouped aggregate). On insert emit '+k,newsum'; on retract
    emit '-k,newsum' (even if newsum==0). Output in event order.
    """
    live = {}
    sums = {}
    emitted = []
    for e in events:
        op = e["op"]
        tid = e["tid"]
        key = e["key"]
        qty = e["qty"]
        attr = e["attr"]
        joins = key in b_keys and (cond_key is None or attr == cond_key)
        if op == "i":
            live[tid] = e
            if joins:
                newv = sums.get(key, 0) + qty
                sums[key] = newv
                emitted.append(("+", key, newv))
        else:
            info = live.pop(tid, None)
            if info is None:
                continue
            old_key = info["key"]
            old_joins = old_key in b_keys and (cond_key is None or info["attr"] == cond_key)
            if old_joins != joins:
                # the tuple left the view entirely on this event
                if joins:
                    newv = sums.get(key, 0) + qty
                    sums[key] = newv
                    emitted.append(("+", key, newv))
                else:
                    newv = sums.get(old_key, 0) - info["qty"]
                    sums[old_key] = newv
                    emitted.append(("-", old_key, newv))
            elif joins:
                newv = sums.get(key, 0) - qty
                sums[key] = newv
                emitted.append(("-", key, newv))
    return emitted


@dataclass
class StreamingViewDeltaConfig(Config):
    n_events: int = 6

    def apply_difficulty(self, level):
        self.n_events = stochastic_rounding(self.n_events + 2 * level)


class StreamingViewDelta(Task):
    summary = "Maintain filtered bag joins and conditional grouped aggregates as base tuples are inserted and retracted, including key replacement and antijoin branches; answer emitted deltas or a queried corrected row."
    design_choice = design_choice
    config_cls = StreamingViewDeltaConfig

    def generate_entry(self):
        n = self.config.n_events
        while True:
            entry = self._gen(n)
            if entry is not None:
                return entry

    def _events(self, n, b_keys):
        """Build an event sequence with insert/retract and key replacement."""
        events = []
        live = {}
        for _ in range(n):
            if not live or random.random() < 0.6:
                tid = random.randrange(0, n + 4)
                key = random.randrange(0, 5)
                qty = random.randint(1, 3)
                attr = random.randint(0, 2)
                if tid in live:
                    old = live.pop(tid)
                    events.append({"op": "r", "tid": tid, "key": old["key"],
                                   "qty": old["qty"], "attr": old["attr"]})
                events.append({"op": "i", "tid": tid, "key": key,
                               "qty": qty, "attr": attr})
                live[tid] = events[-1]
            else:
                rk = random.choice(list(live))
                old = live.pop(rk)
                events.append({"op": "r", "tid": rk, "key": old["key"],
                               "qty": old["qty"], "attr": old["attr"]})
        return events

    def _gen(self, n):
        b_keys = set(random.sample(range(0, 5), random.randint(1, 4)))
        events = self._events(n, b_keys)
        if random.random() < 0.5:
            mode = "delta"
            cond_key = random.choice([None, 0, 1, 2]) if random.random() < 0.5 else None
            emitted = _simulate(events, b_keys, cond_key)
            if not emitted:
                return None
            lines = "\n".join(f"{s}{k},{v}" for s, k, v in emitted)
            return Entry(metadata={"kind": "delta", "cond_key": cond_key,
                                   "b_keys": sorted(b_keys), "events": events},
                         answer=lines)
        else:
            finals = {k: self._query_value(events, b_keys, k) for k in b_keys}
            pos = [k for k, v in finals.items() if v > 0]
            if not pos:
                return None
            qk = random.choice(pos)
            val = finals[qk]
            return Entry(metadata={"kind": "query", "cond_key": None,
                                   "b_keys": sorted(b_keys), "events": events,
                                   "query_key": qk},
                         answer=str(val))

    def _query_value(self, events, b_keys, qk):
        if qk not in b_keys:
            return 0
        live = {}
        tot = 0
        for e in events:
            op = e["op"]
            tid = e["tid"]
            key = e["key"]
            qty = e["qty"]
            if op == "i":
                live[tid] = key
                if key == qk:
                    tot += qty
            else:
                if tid in live:
                    if live[tid] == qk:
                        tot -= qty
                    del live[tid]
        return tot

    def _render_payload(self, metadata):
        ev = metadata["events"]
        lines = ["B = {" + ", ".join(str(k) for k in metadata["b_keys"]) + "}"]
        for i, e in enumerate(ev):
            op = "insert" if e["op"] == "i" else "retract"
            lines.append(f"{i+1}. {op} A(t{e['tid']}, key={e['key']}, "
                         f"qty={e['qty']}, attr={e['attr']})")
        body = "\n".join(lines)
        cond = metadata["cond_key"]
        if metadata["kind"] == "delta":
            if cond is None:
                head = ("A streaming bag-join view joins A with B on key; "
                        "an A tuple contributes to key k's sum only if k is "
                        "present in B. As A tuples are inserted and "
                        "retracted, the per-key sum changes. Each time a "
                        "key's sum changes, emit one delta line: '+k,v' when "
                        "it rises to new value v, or '-k,v' when it falls. "
                        "Emit lines in event order, one per change, separated "
                        "by newlines. When a key's sum becomes 0, emit "
                        "'-k,0'.")
            else:
                head = (f"A streaming bag-join view joins A with B on key and "
                        f"then aggregates per key the sum of qty of live A "
                        f"tuples whose attr equals {cond} (other A tuples are "
                        f"filtered out entirely). A key also must be present "
                        f"in B. Each time a key's grouped sum changes emit a "
                        f"delta line '+k,v' (rise) or '-k,v' (fall), in event "
                        f"order, one per change, newline-separated. When a "
                        f"key's sum becomes 0 emit '-k,0'.")
            return f"{head}\n{body}\n\nDeltas:"
        else:
            qk = metadata["query_key"]
            head = ("A streaming bag-join view joins A with B on key; an A "
                    "tuple contributes to key k's sum only if k is in B. As "
                    "tuples are inserted and retracted (in event order), each "
                    "key's sum changes; a later insert with a new key is a "
                    "key replacement but each key keeps its own independent "
                    "running sum. After processing every event, report the "
                    "final corrected value (a non-negative integer) for the "
                    "queried key.")
            return f"{head}\n{body}\n\nQuery: final corrected value for key {qk}?"

    def render_prompt(self, metadata):
        return self._render_payload(metadata)

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        if metadata["kind"] == "delta":
            return 1.0 if answer.strip() == entry.answer.strip() else 0.0
        else:
            try:
                return 1.0 if int(answer.strip()) == int(entry.answer) else 0.0
            except ValueError:
                return 0.0
