"""Trace a small stateful system through a sequence of operations under explicitly stated rules.

Unifies five generated trace tasks that each ranked in the top 10 on v8_tiny but covered one
mechanism apiece: cache_replacement_trace, rate_limit_token_bucket, heap_key_update, interval_sweep
and two_phase_commit_trace. One task with a system drawn per instance keeps their shared skill
(apply stated rules step by step, keep the state exact) and spreads it over five state shapes.
Changes on the way in: the heap runs a sequence of operations instead of one sift; two-phase
commit adds a coordinator crash, blocked participants and cooperative termination (the original's
answers were almost all abort); intervals are half-open, so touching does not mean overlapping.
"""
import heapq
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, edict, stochastic_rounding as sround

SYSTEMS = ("cache", "bucket", "heap", "commit", "sweep")


@dataclass
class SystemsTraceConfig(Config):
    size: int = 1

    def apply_difficulty(self, level):
        self.size = 1 + level


def _cache(n):
    cap = 2 + sround(n / 3)
    keys = list(range(cap + 2 + n // 2))
    seq = [random.choice(keys) for _ in range(6 + 2 * n)]
    policy = random.choice(["LRU", "FIFO", "LFU"])
    resident, inserted, last, freq, evicted, misses = [], {}, {}, {}, [], 0
    for t, k in enumerate(seq):
        if k in resident:
            freq[k] += 1
        else:
            misses += 1
            if len(resident) == cap:
                if policy == "LRU":
                    victim = min(resident, key=lambda r: last[r])
                elif policy == "FIFO":
                    victim = min(resident, key=lambda r: inserted[r])
                else:
                    victim = min(resident, key=lambda r: (freq[r], last[r]))
                resident.remove(victim)
                evicted.append(victim)
            resident.append(k)
            inserted[k], freq[k] = t, 1
        last[k] = t
    rule = {"LRU": "evict the resident key whose most recent access is oldest",
            "FIFO": "evict the resident key that was inserted earliest",
            "LFU": "evict the resident key with the fewest accesses since it was last inserted; on a tie, "
                   "the one among them whose most recent access is oldest"}[policy]
    q = random.choice(["misses", "evicted", "final"] if evicted else ["misses", "final"])
    text = (f"A cache holds at most {cap} keys and starts empty. On an access, a key already in the cache is a "
            f"hit; otherwise it is a miss and the key is inserted, and if the cache is full you first {rule} "
            f"({policy}). Accesses, in order: {' '.join(map(str, seq))}.\n")
    if q == "misses":
        return text + "How many accesses are misses? Answer with a number.", str(misses)
    if q == "evicted":
        return (text + "List the evicted keys in the order they were evicted, separated by spaces.",
                " ".join(map(str, evicted)))
    return (text + "Which keys are in the cache at the end? List them in increasing order, separated by spaces.",
            " ".join(map(str, sorted(resident))))


def _bucket(n):
    cap, period, refill = random.randint(3, 8), random.randint(2, 4), random.randint(1, 3)
    tokens = random.randint(0, cap)
    times = sorted(random.sample(range(1, 4 + 4 * n + 6), 3 + n))
    reqs = [(t, random.randint(1, 4)) for t in times]
    text = (f"A token bucket holds at most {cap} tokens and starts with {tokens}. At every time that is a "
            f"multiple of {period} (time {period}, {2 * period}, ...), {refill} tokens are added, never going "
            f"above {cap}; at a time with both a refill and a request, the refill comes first. A request is "
            "accepted if the bucket holds at least its cost, and then the cost is removed; otherwise it is "
            "rejected and nothing is removed.\nRequests (time: cost): "
            + ", ".join(f"{t}: {c}" for t, c in reqs) + ".\n")
    now, accepted = 0, []
    for t, c in reqs:
        tokens = min(cap, tokens + refill * (t // period - now // period))
        now = t
        if tokens >= c:
            tokens -= c
            accepted.append(t)
    q = random.choice(["accepted", "balance"])
    if q == "accepted":
        return (text + "List the times of the accepted requests in increasing order, separated by spaces "
                "(write none if no request is accepted).", " ".join(map(str, accepted)) or "none")
    return text + "How many tokens are in the bucket right after the last request? Answer with a number.", str(tokens)


def _sift_up(h, i):
    while i and h[(i - 1) // 2] > h[i]:
        h[i], h[(i - 1) // 2] = h[(i - 1) // 2], h[i]
        i = (i - 1) // 2


def _sift_down(h, i):
    while True:
        kids = [c for c in (2 * i + 1, 2 * i + 2) if c < len(h)]
        if not kids:
            return
        c = min(kids, key=lambda k: h[k])
        if h[c] >= h[i]:
            return
        h[i], h[c] = h[c], h[i]
        i = c


def _heap(n):
    pool = random.sample(range(10, 100), 30)
    h = pool[:5 + n]
    heapq.heapify(h)
    fresh = pool[5 + n:]
    start, ops, popped = list(h), [], []
    for _ in range(3 + n):
        kind = random.choice(["insert", "extract", "decrease"] if h else ["insert"])
        if kind == "insert":
            x = fresh.pop()
            h.append(x)
            _sift_up(h, len(h) - 1)
            ops.append(f"insert {x}")
        elif kind == "extract":
            popped.append(h[0])
            h[0] = h[-1]
            h.pop()
            if h:
                _sift_down(h, 0)
            ops.append("extract-min")
        else:
            i = random.randrange(len(h))
            lower = [v for v in range(1, h[i]) if v not in h and v not in fresh]
            if not lower:
                continue
            v = random.choice(lower[-12:])
            ops.append(f"decrease the key at index {i} (currently {h[i]}) to {v}")
            h[i] = v
            _sift_up(h, i)
    text = (f"A binary min-heap is stored as a 0-based array (the children of index i are 2i+1 and 2i+2): "
            f"{start}.\nApply in order: " + "; ".join(ops) + ".\n"
            "insert appends the key and sifts it up; extract-min removes the root, moves the last element to the "
            "root and sifts it down, swapping with the smaller child; decrease sets the key and sifts it up.\n")
    if popped and random.random() < 0.4:
        return (text + "Which keys does extract-min return, in order? Separate them with spaces.",
                " ".join(map(str, popped)))
    return text + "What is the final array? Write it like [1, 2, 3].", str(h)


def _commit(n):
    parts = [f"P{i + 1}" for i in range(3 + n // 2)]
    vote = {p: "yes" for p in parts}
    if random.random() < 0.5:
        # One dissenter (rarely two): with more, every reachable group learns abort and states go uniform.
        for p in random.sample(parts, random.choice([1, 1, 1, 2])):
            vote[p] = random.choice(["no", "crash"])
    decision = "commit" if all(v == "yes" for v in vote.values()) else "abort"
    order = random.sample(parts, len(parts))
    sent = order[:random.randint(0, len(parts))]
    coop = random.random() < 0.7
    # Cooperative termination only reaches participants on the same side of a network partition.
    side = {p: random.random() < 0.5 for p in parts} if coop and random.random() < 0.7 else {p: True for p in parts}
    know = {p: decision for p in sent if vote[p] == "yes"}
    know.update({p: "abort" for p in parts if vote[p] != "yes"})
    state = {}
    for p in parts:
        peers = [know[q] for q in know if side[q] == side[p]]
        if p in know:
            state[p] = know[p][0].upper()
        elif coop and peers:
            state[p] = peers[0][0].upper()
        else:
            state[p] = "B"
    # All-commit or all-abort is what every 2PC run converges to without crashes; keep a minority of them.
    if len(set(state.values())) == 1 and random.random() < 0.75:
        return None
    vote_text = "; ".join(f"{p} {'votes yes' if v == 'yes' else 'votes no' if v == 'no' else 'crashes before voting'}"
                          for p, v in vote.items())
    crash = (f"The coordinator sends its decision to {', '.join(sent)} in that order and then crashes"
             if len(sent) < len(parts) else f"The coordinator sends its decision to every participant")
    if not sent and len(sent) < len(parts):
        crash = "The coordinator crashes right after deciding, before sending the decision to anyone"
    text = (f"Two-phase commit with a coordinator and participants {', '.join(parts)}. The coordinator asks "
            f"each participant to vote: {vote_text}. The coordinator decides commit only if every participant "
            f"votes yes; otherwise it decides abort (a missing vote counts as no). {crash}.\n"
            "A participant that votes no or crashed before voting aborts on its own. A participant that voted "
            "yes adopts the decision if it receives it; otherwise it is blocked"
            + (", unless cooperative termination applies: it asks the participants it can reach, and if any of "
               "them has aborted on its own or received the decision, it adopts that outcome." if coop else
               ". There is no cooperative termination.")
            + (f" A network partition splits the participants into {{{', '.join(p for p in parts if side[p])}}} and "
               f"{{{', '.join(p for p in parts if not side[p])}}}; each can reach only its own group."
               if coop and len(set(side.values())) == 2 else "")
            + "\nGive the final state of each participant in order as C (committed), A (aborted) or B "
            "(blocked), like P1:C P2:B")
    return text, " ".join(f"{p}:{state[p]}" for p in parts)


def _sweep(n):
    ivs = []
    for _ in range(4 + n):
        s = random.randint(0, 20 + 6 * n)
        ivs.append((s, s + random.randint(1, 8 + n)))
    events = sorted([(s, 1) for s, _ in ivs] + [(e, -1) for _, e in ivs], key=lambda x: (x[0], x[1]))
    cur = peak = 0
    for _, d in events:
        cur += d
        peak = max(peak, cur)
    merged = []
    for s, e in sorted(ivs):
        if merged and s < merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    text = ("Intervals are half-open: [s, e) contains every x with s <= x < e, so intervals that only touch "
            f"do not overlap. Intervals: {', '.join(f'[{s}, {e})' for s, e in ivs)}.\n")
    q = random.choice(["peak", "length", "merged"])
    if q == "peak":
        return text + "What is the largest number of intervals that contain a common point? Answer with a number.", str(peak)
    if q == "length":
        return (text + "What is the total length of their union? Answer with a number.",
                str(sum(e - s for s, e in merged)))
    return (text + "Merge overlapping intervals (touching ones stay separate) and list the result in increasing "
            "order like [1, 4) [4, 6) [8, 9).", " ".join(f"[{s}, {e})" for s, e in merged))


class SystemsTrace(DevTask):
    summary = ("Trace a stateful system under explicit rules -- an LRU/FIFO/LFU cache, a token-bucket rate "
               "limiter, a binary min-heap, two-phase commit with a coordinator crash, or a half-open interval "
               "sweep -- and report a count, the sequence of outputs, or the final state.")
    config_cls = SystemsTraceConfig
    task_version = 1

    def generate_entry(self):
        system = random.choice(SYSTEMS)
        out = None
        while out is None:  # redraw within the system, so rejections do not skew the system mix
            out = globals()[f"_{system}"](self.config.size)
        prompt, answer = out
        return Entry(metadata=edict(system=system, prompt=prompt), answer=answer)

    def render_prompt(self, m):
        return m.prompt

    def score_answer(self, answer, entry):
        norm = lambda x: " ".join(str(x).replace(",", " ").split()).lower()
        return float(norm(answer) == norm(entry.answer))
