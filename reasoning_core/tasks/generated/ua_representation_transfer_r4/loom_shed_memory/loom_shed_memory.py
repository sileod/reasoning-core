import random
from dataclasses import dataclass

from reasoning_core.template import Task, Entry, Config, edict, render_payload, stochastic_rounding as sround

TASK_META = {'parent_source_id': None,
 'idea': 'loom_shed_memory (variant 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_representation_transfer_r4/loom_shed_memory',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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


def _simulate(ops, pedals):
    latched = set()
    sheds = []
    for op in ops:
        kind = op[0]
        if kind == 'press':
            latched = latched | set(pedals[op[1]])
        elif kind == 'release':
            latched = latched - set(op[1])
        sheds.append(frozenset(latched))
    return sheds


def _random_tieup(n_shafts):
    size = random.randrange(1, n_shafts + 1)
    return tuple(sorted(random.sample(range(n_shafts), size)))


def _cross_order(n_picks, reversal_pair):
    if reversal_pair is None:
        return list(range(n_picks))
    p, q = reversal_pair
    return list(range(0, p + 1)) + list(range(q, p, -1)) + list(range(q + 1, n_picks))


def _count_floats(sheds, threading, crossing, threshold):
    n_warps = len(threading)
    count = 0
    for w in range(n_warps):
        sh = threading[w]
        run = 0
        for idx in crossing:
            if sh not in sheds[idx]:
                run += 1
            else:
                if run > threshold:
                    count += 1
                run = 0
        if run > threshold:
            count += 1
    return count


@dataclass
class LoomShedMemoryV2Config(Config):
    n_warps: int = 5
    n_shafts: int = 3
    n_pedals: int = 3
    n_picks: int = 6
    threshold: int = 2
    reversal_prob: float = 0.25
    allow_reversal: bool = True

    def apply_difficulty(self, level):
        self.n_warps = sround(self.n_warps + level)
        self.n_shafts = sround(self.n_shafts + level)
        self.n_pedals = sround(self.n_pedals + level)
        self.n_picks = sround(self.n_picks + 2 * level)
        self.threshold = max(1, sround(2 + level))
        self.reversal_prob = min(0.8, 0.2 + 0.1 * level)
        self.allow_reversal = level >= 1


class LoomShedMemory(Task):
    config_cls = LoomShedMemoryV2Config
    summary = ("Execute loom picks with shaft threading, pedal tie-ups, latched lifts, "
               "explicit releases, and reversed shuttle passes; determine queried "
               "over-under crossings or uninterrupted floats in the resulting cloth.")
    design_choice = ("Answers are single integers counting uninterrupted floats "
                     "exceeding a threshold, with difficulty from explicit release "
                     "timing and reversed pass ordering.")

    def generate_entry(self):
        cfg = self.config
        while True:
            n_warps = cfg.n_warps
            n_shafts = cfg.n_shafts
            n_picks = cfg.n_picks
            threading = [random.randrange(n_shafts) for _ in range(n_warps)]
            if len(set(threading)) < n_shafts:
                continue
            pedals = []
            for _ in range(cfg.n_pedals):
                pedals.append(_random_tieup(n_shafts))
            if not any(pedals):
                pedals = [(0,)]
            latched = set()
            ops = []
            for _ in range(n_picks):
                roll = random.random()
                if roll < 0.20:
                    ops.append(('hold', ()))
                elif roll < 0.60:
                    pidx = random.randrange(len(pedals))
                    tieup = pedals[pidx]
                    ops.append(('press', pidx))
                    latched = latched | set(tieup)
                elif latched:
                    k = random.randint(1, len(latched))
                    dropped = tuple(sorted(random.sample(sorted(latched), k)))
                    ops.append(('release', dropped))
                    latched = latched - set(dropped)
                else:
                    pidx = random.randrange(len(pedals))
                    tieup = pedals[pidx]
                    ops.append(('press', pidx))
                    latched = latched | set(tieup)
            sheds = _simulate(ops, pedals)
            reversal_pair = None
            if cfg.allow_reversal and n_picks >= 3 and random.random() < cfg.reversal_prob:
                p = random.randrange(0, n_picks - 1)
                q = random.randrange(p + 1, n_picks)
                reversal_pair = (p, q)
            crossing = _cross_order(n_picks, reversal_pair)
            answer = _count_floats(sheds, threading, crossing, cfg.threshold)
            if answer < 0:
                continue
            recomputed = _count_floats(sheds, threading, crossing, cfg.threshold)
            if recomputed != answer:
                raise RuntimeError("float count unstable")
            break

        pedal_names = "ABCDEFGHJKLMNPQR"
        meta = edict({
            "n_warps": n_warps,
            "n_shafts": n_shafts,
            "n_picks": n_picks,
            "threading": threading,
            "pedals": [list(t) for t in pedals],
            "ops": [(o[0], o[1]) for o in ops],
            "reversal_pair": None if reversal_pair is None else list(reversal_pair),
            "crossing": crossing,
            "threshold": cfg.threshold,
            "answer": answer,
        })
        meta.payload = {
            "threading": threading,
            "pedals": [list(t) for t in pedals],
            "ops": [(o[0], o[1]) for o in ops],
            "reversal_pair": None if reversal_pair is None else list(reversal_pair),
            "threshold": cfg.threshold,
            "pedal_names": list(pedal_names),
        }
        return Entry(metadata=meta, answer=str(answer))

    def render_prompt(self, metadata):
        threading = metadata.payload["threading"]
        pedals = metadata.payload["pedals"]
        ops = metadata.payload["ops"]
        reversal_pair = metadata.payload["reversal_pair"]
        threshold = metadata.payload["threshold"]
        n_shafts = threading and max(threading) + 1
        pedal_names = metadata.payload["pedal_names"]
        thread_part = ", ".join(
            "warp %d -> shaft %d" % (i + 1, sh) for i, sh in enumerate(threading)
        )
        pedal_part = "; ".join(
            "pedal %s lifts shafts %s" % (pedal_names[i], ",".join(
                str(sh + 1) for sh in tieup))
            for i, tieup in enumerate(pedals)
        )
        op_part = []
        for i, (kind, arg) in enumerate(ops):
            if kind == 'press':
                op_part.append("pick %d: press pedal %s" % (i + 1, pedal_names[arg]))
            elif kind == 'release':
                op_part.append("pick %d: release shafts %s" % (
                    i + 1, ",".join(str(sh + 1) for sh in arg)))
            else:
                op_part.append("pick %d: no change (shed holds)" % (i + 1))
        ops_text = "; ".join(op_part)
        if reversal_pair is None:
            order_text = ("The shuttle crosses every pick in the order listed, from "
                          "pick 1 through pick %d." % len(ops))
        else:
            p, q = reversal_pair
            order_text = ("The shuttle crosses picks 1 through %d in order, then it "
                          "reverses and crosses picks %d back down to %d, then continues "
                          "to the end. Use this order for measuring runs." % (
                              p + 1, q + 1, p + 2))
        return (
            "A loom has %d warp threads. %s. There are %d pedals; pressing a pedal lifts "
            "its shafts and that lift latches, meaning it stays up until explicitly "
            "released. %s. The weaver starts with no shaft lifted. %s. When the shed is "
            "formed the shuttle lays the weft over the warps whose shaft is NOT lifted "
            "(those warps stay down) and under the lifted warps. %s "
            "A float on a warp is a run of consecutive crossings (in that crossing "
            "order) where the warp stays down, i.e. the weft lies over it. "
            "Count how many warp-floats have length strictly greater than %d. "
            "Give the answer as a single integer." % (
                len(threading), thread_part, len(pedals), pedal_part, ops_text,
                order_text, threshold)
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        answer = answer.strip()
        if not answer.lstrip("-").isdigit():
            return 0.0
        return 1.0 if int(answer) == int(entry.answer) else 0.0
