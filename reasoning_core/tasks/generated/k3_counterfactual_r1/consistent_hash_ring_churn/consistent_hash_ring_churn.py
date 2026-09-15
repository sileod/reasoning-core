import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


def _num(level, base, growth):
    return max(1, int(base + growth * level))


TASK_META = {'parent_source_id': None,
 'idea': 'consistent_hash_ring_churn (draw 2 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_counterfactual_r1/consistent_hash_ring_churn',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2701974858,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class ConsistentHashRingChurnV2Config(Config):
    num_keys: int = 4
    num_initial_nodes: int = 3
    num_joins: int = 1
    num_failures: int = 1
    ring_size: int = 24

    def apply_difficulty(self, level):
        self.num_keys = _num(level, 4, 3)
        self.num_initial_nodes = _num(level, 3, 1)
        self.num_joins = _num(level, 1, 1)
        self.num_failures = _num(level, 1, 1)
        self.ring_size = 24 + 8 * level


def _successor(point, nodes):
    for node in sorted(nodes):
        if node >= point:
            return node
    if nodes:
        return min(nodes)
    return None


def _parse_answer(answer):
    if not isinstance(answer, str) or not answer.startswith("moved=") or " unchanged=" not in answer:
        return None
    moved, unchanged = answer[6:].split(" unchanged=", 1)
    moved_parsed = []
    if moved != "none":
        for spec in moved.split("; "):
            rng, rest = spec.split("@", 1)
            lo, hi = rng[1:-1].split(",")
            lo, hi = int(lo), int(hi)
            transp = []
            for t in rest.split(","):
                pp, rest2 = t.split(":")
                cur, new = rest2.split("->")
                transp.append((int(pp), int(cur), int(new)))
            moved_parsed.append((lo, hi, transp))
    unchanged_parsed = []
    if unchanged != "none":
        for spec in unchanged.split("; "):
            rng, owner = spec.split(": ", 1)
            lo, hi = rng[1:-1].split(",")
            unchanged_parsed.append((int(lo), int(hi), int(owner)))
    return moved_parsed, unchanged_parsed


def _compare_answer(answer, entry):
    parsed = _parse_answer(answer)
    if parsed is None:
        return 0.0
    moved, unchanged = parsed
    meta = entry.metadata
    exp_moved = [(lo, hi, [(pp, c, n) for (pp, c, n) in per]) for (lo, hi, per) in meta["moved_ranges"]]
    exp_unchanged = [(lo, hi, o) for (lo, hi, o) in meta["unchanged_ranges"]]
    if moved == exp_moved and unchanged == exp_unchanged:
        return 1.0
    return 0.0


class ConsistentHashRingChurn(Task):
    summary = "Place keys and nodes at given ring positions with successor ownership, process node joins and failures, and answer which key ranges move and each key's new owner while untouched ranges stay put."
    design_choice = "Represent keys as contiguous ranges with variable lengths, so moves are reported per range, and untouched ranges are explicitly listed as unchanged."
    config_cls = ConsistentHashRingChurnV2Config
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        ring_size = cfg.ring_size

        intervals = []
        for _ in range(cfg.num_keys - 1):
            lo = intervals[-1][1] if intervals else 0
            remaining = ring_size - lo
            if remaining < 2:
                break
            length = random.randint(1, remaining - 1)
            intervals.append((lo, lo + length))
        if intervals:
            lo = intervals[-1][1]
            if lo < ring_size:
                intervals.append((lo, ring_size))

        initial_nodes = []
        for _ in range(cfg.num_initial_nodes):
            c = random.randint(0, ring_size - 1)
            while c in initial_nodes:
                c = random.randint(0, ring_size - 1)
            initial_nodes.append(c)
        initial_nodes = sorted(initial_nodes)

        events = []
        working = list(initial_nodes)
        target = cfg.num_joins + cfg.num_failures
        resample = True
        while resample:
            resample = False
            events = []
            working = list(initial_nodes)
            guard = 0
            while len(events) < target and guard < 5000:
                guard += 1
                action = random.choice(["join", "failure"])
                if action == "join":
                    if len(working) >= ring_size:
                        continue
                    c = random.randint(0, ring_size - 1)
                    ng = 0
                    while c in working and ng < 1000:
                        c = random.randint(0, ring_size - 1)
                        ng += 1
                    if c in working:
                        continue
                    working.append(c)
                    events.append(("join", c))
                else:
                    if not working:
                        continue
                    c = random.choice(working)
                    working.remove(c)
                    events.append(("failure", c))
            events = events[:target]
            working2 = list(initial_nodes)
            for (a, n) in events:
                if a == "join":
                    working2.append(n)
                else:
                    if not working2:
                        resample = True
                        break
                    working2.remove(n)
            if not working2:
                resample = True

        final_nodes = sorted(working)

        def owners(nodes):
            return [_successor(pt, nodes) for pt in range(ring_size)]

        moved_ranges = []
        unchanged = []
        for (lo, hi) in intervals:
            lo = int(lo)
            hi = int(hi)
            p = lo
            while p < hi:
                old = _successor(p, initial_nodes)
                new = _successor(p, final_nodes)
                if new == old:
                    start = p
                    while p < hi and _successor(p, initial_nodes) == _successor(p, final_nodes) == old:
                        p += 1
                    unchanged.append((start, p, old))
                else:
                    start = p
                    per = []
                    while p < hi and (
                        _successor(p, initial_nodes) != _successor(p, final_nodes)
                    ):
                        per.append((p, _successor(p, initial_nodes), _successor(p, final_nodes)))
                        p += 1
                    moved_ranges.append((start, p, per))
        moved_ranges = [m for m in moved_ranges if m[2]]
        unchanged = [u for u in unchanged]

        moved_part = []
        for (lo, hi, per) in moved_ranges:
            moved_part.append("[%d,%d)@" % (lo, hi) + ",".join("%d:%d->%d" % (p, c, n) for (p, c, n) in per))
        unchanged_part = []
        for (lo, hi, owner) in unchanged:
            unchanged_part.append("[%d,%d): %d" % (lo, hi, owner))
        moved_out = "; ".join(moved_part) if moved_part else "none"
        unchanged_out = "; ".join(unchanged_part) if unchanged_part else "none"
        answer = "moved=%s unchanged=%s" % (moved_out, unchanged_out)

        metadata = {
            "ring_size": ring_size,
            "initial_nodes": initial_nodes,
            "events": [[a, n] for (a, n) in events],
            "intervals": [list(iv) for iv in intervals],
            "final_nodes": final_nodes,
            "moved_ranges": [[lo, hi, [[pp, c, n] for (pp, c, n) in per]] for (lo, hi, per) in moved_ranges],
            "unchanged_ranges": [[lo, hi, o] for (lo, hi, o) in unchanged],
        }

        for (lo, hi, per) in moved_ranges:
            for (p, cur, new) in per:
                assert _successor(p, final_nodes) == new
                assert _successor(p, initial_nodes) == cur
        for (lo, hi, owner) in unchanged:
            for p in range(lo, hi):
                assert _successor(p, final_nodes) == _successor(p, initial_nodes) == owner

        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        lines = []
        lines.append("A consistent hash ring has positions 0..%d. Each position is owned by the first node at or after it, wrapping around to the lowest node if none exists." % (metadata["ring_size"] - 1))
        lines.append("Initial node positions: %s." % sorted(metadata["initial_nodes"]))
        evs = "; ".join("%s node %d" % (a, n) for (a, n) in metadata["events"])
        lines.append("Then these churn events happen, in order, updating the node set: %s." % evs)
        lines.append("Keys occupy contiguous ranges: %s." % "; ".join("[%d,%d)" % (lo, hi) for (lo, hi) in metadata["intervals"]))
        lines.append("For each range, report which positions change owner (as '[lo,hi)@position:old->new,...' where positions in the range are comma-separated) grouped under 'moved=...', and list ranges with no ownership change (as '[lo,hi): owner') under 'unchanged=...'. Ranges that stay put are explicitly listed under unchanged. Use format: moved=<list> unchanged=<list>; write 'none' for either if empty.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        return _compare_answer(answer, entry)
