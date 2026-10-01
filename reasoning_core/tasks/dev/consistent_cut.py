"""Find the orphans of a global cut in a message-passing run, or roll it back to a consistent one.

Reworked from the generated consistent_distributed_cut (ext #4, margin #2 on v8_tiny). That version
counted messages "sent inside the cut and received outside" -- in-transit messages, which a
consistent cut allows -- under the name orphan, and drew send and receive positions independently,
so its runs were not executions (a message could be received before anything was sent). Here the
run is simulated, an orphan is a message received inside the cut but sent outside it, and the
harder question asks for the largest consistent cut inside the given one: excluding an orphan's
receive can exclude a later send whose receive must then go too, so the rollback cascades.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, edict, stochastic_rounding as sround


@dataclass
class ConsistentCutConfig(Config):
    n_procs: int = 3
    events: int = 5
    p_rollback: float = 0.7

    def apply_difficulty(self, level):
        self.n_procs = min(5, 3 + sround(level / 3))
        self.events = 5 + level
        self.p_rollback = min(0.9, 0.7 + 0.04 * level)


def _simulate(n, per_proc):
    """Per-process event lists; messages: id -> [src, send_pos, dst, recv_pos or None] (1-based)."""
    events = [[] for _ in range(n)]
    msgs, pending = {}, []
    while min(len(e) for e in events) < per_proc:
        p = random.choice([q for q in range(n) if len(events[q]) < per_proc])
        inbox = [m for m in pending if msgs[m][2] == p]
        r = random.random()
        if inbox and r < 0.45:
            m = random.choice(inbox)
            pending.remove(m)
            events[p].append(("recv", m))
            msgs[m][3] = len(events[p])
        elif r < 0.85:
            m = len(msgs) + 1
            dst = random.choice([q for q in range(n) if q != p])
            events[p].append(("send", m))
            msgs[m] = [p, len(events[p]), dst, None]
            pending.append(m)
        else:
            events[p].append(("local", None))
    return events, msgs


def _orphans(msgs, cut):
    return sorted(m for m, (src, sp, dst, rp) in msgs.items()
                  if rp is not None and rp <= cut[dst] and sp > cut[src])


def _rollback(msgs, cut):
    cut, rounds = list(cut), 0
    while orphans := _orphans(msgs, cut):
        rounds += 1
        for m in orphans:
            cut[msgs[m][2]] = min(cut[msgs[m][2]], msgs[m][3] - 1)
    return cut, rounds


class ConsistentCut(DevTask):
    summary = ("Given the event sequences of a message-passing run and a global cut (a prefix of each "
               "process), report how many messages are orphans (received inside the cut, sent outside), "
               "or the largest consistent cut contained in it.")
    config_cls = ConsistentCutConfig
    task_version = 1

    def generate_entry(self):
        cfg = self.config
        events, msgs = _simulate(cfg.n_procs, cfg.events)
        cut = [random.randint(0, len(e)) for e in events]
        orphans = _orphans(msgs, cut)
        if random.random() < cfg.p_rollback:
            if not orphans:
                return None
            fixed, rounds = _rollback(msgs, cut)
            # Most cuts settle in one round; keep more of the cascades as the level rises.
            if rounds == 1 and random.random() < min(0.7, 0.12 * cfg.level):
                return None
            mode, answer = "rollback", " ".join(f"P{p}:{c}" for p, c in enumerate(fixed))
        else:
            # Small runs mostly have 0 or 1 orphans, a free constant guess; keep 1 at a reduced rate.
            if not orphans or len(orphans) == 1 and random.random() < 0.6:
                return None
            mode, answer, rounds = "count", str(len(orphans)), 0
        lines = []
        for p, evs in enumerate(events):
            out = []
            for i, (kind, m) in enumerate(evs, 1):
                if kind == "send":
                    out.append(f"{i}. send m{m} to P{msgs[m][2]}")
                elif kind == "recv":
                    out.append(f"{i}. receive m{m} from P{msgs[m][0]}")
                else:
                    out.append(f"{i}. local step")
            lines.append(f"P{p}: " + "; ".join(out))
        meta = edict(lines=lines, cut=cut, mode=mode, rounds=rounds, n_orphans=len(orphans))
        return Entry(metadata=meta, answer=answer)

    def render_prompt(self, m):
        cut = " ".join(f"P{p}:{c}" for p, c in enumerate(m.cut))
        head = ("Processes exchange messages. Each process's events are listed in order (event 1 happens "
                "first):\n" + "\n".join(m.lines) + "\n\n"
                f"A global cut keeps the first k events of each process: {cut}.\n"
                "A message is an orphan of a cut when its receive event is inside the cut but its send "
                "event is not. A cut is consistent when it has no orphan.\n")
        if m.mode == "count":
            return head + "How many messages are orphans of this cut? Answer with a number."
        return head + ("What is the largest consistent cut that keeps no more than the given cut on each "
                       "process? Answer in the same format as the cut, for example P0:2 P1:0 P2:3")

    def score_answer(self, answer, entry):
        return float(" ".join(str(answer).replace(",", " ").split()) == entry.answer)

    def balancing_key(self, problem):
        return problem.metadata.mode + ":" + problem.answer
