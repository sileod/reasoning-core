from dataclasses import dataclass
import itertools
import math
import random

from reasoning_core.template import Task, Entry, Config, edict

TASK_META = {'parent_source_id': None,
 'idea': 'geometric_orientation_entailment (variant 1 of 3)',
 'hypothesis': 'P011',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_inference_modes_r4/geometric_orientation_entailment',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2305351643,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

VALID_INFOS = {"cw", "ccw", "alternatives"}


def _cross_sign(seq, a, b, c):
    n = len(seq)
    ta = 2.0 * math.pi * seq.index(a) / n
    tb = 2.0 * math.pi * seq.index(b) / n
    tc = 2.0 * math.pi * seq.index(c) / n
    ax, ay = math.cos(ta), math.sin(ta)
    bx, by = math.cos(tb), math.sin(tb)
    cx, cy = math.cos(tc), math.sin(tc)
    val = (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)
    if val > 0:
        return "cw"
    return "ccw"


def _triples(labels):
    return list(itertools.combinations(sorted(labels), 3))


def _calc_answer(labels, order, revealed, query):
    consistent = []
    target_signs = {t: _cross_sign(order, *t) for t in revealed}
    for perm in itertools.permutations([l for l in labels if l != order[0]]):
        seq = (order[0],) + tuple(perm)
        ok = True
        for t in revealed:
            if _cross_sign(seq, *t) != target_signs[t]:
                ok = False
                break
        if ok:
            consistent.append(_cross_sign(seq, *query))
    if not consistent:
        raise RuntimeError("no consistent order")
    vals = set(consistent)
    if len(vals) == 1:
        return next(iter(vals))
    return "alternatives"


@dataclass
class GeoOrientationEntailmentConfig(Config):
    def apply_difficulty(self, level):
        self.level = level


class GeometricOrientationEntailment(Task):
    summary = ("Complete partial triple-orientation (clockwise/counterclockwise sidedness) data for "
               "labeled planar points in convex position under collinearity, convexity and sidedness "
               "constraints; answer the forced orientation of a queried triple or whether alternatives "
               "remain.")
    design_choice = ("Instance difficulty from sparse vs. dense partial constraints: random subset of "
                     "triples vs. all triples except a few omitted")
    config_cls = GeoOrientationEntailmentConfig
    task_version = 2

    def generate_entry(self):
        level = self.config.level
        n = 5 + (level // 2)
        density = 0.35 + 0.60 * (level / 6.0)
        labels = ["ABCDEFGH"[i] for i in range(n)]
        order = labels[:]
        random.shuffle(order)
        all_triples = _triples(labels)
        total = len(all_triples)
        revealed_count = max(2, min(total - 2, int(round(density * total))))
        reveal_pool = all_triples[:]
        random.shuffle(reveal_pool)
        revealed = set(reveal_pool[:revealed_count])
        remaining = [t for t in all_triples if t not in revealed]
        query = random.choice(remaining)
        answer = _calc_answer(labels, order, sorted(revealed), query)

        facts = sorted((tuple(t), _cross_sign(order, *t)) for t in revealed)
        payload = {"given": facts, "query": list(query)}
        metadata = edict({
            "n": n,
            "labels": labels,
            "revealed": [[list(t), s] for t, s in facts],
            "query": list(query),
            "density": float(density),
        })
        metadata.payload = payload
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        payload = metadata.payload
        lines = []
        for t, s in payload["given"]:
            lines.append(f"   {t[0]}, {t[1]}, {t[2]}: {s}")
        q = payload["query"]
        header = (
            "A set of labeled planar points lies on the boundary of a common convex hull, so every "
            "triple of points is either a clockwise (cw) or counterclockwise (ccw) turn. Below are the "
            "known orientation facts for some triples of points. If they force a single orientation for "
            "the queried triple, reply cw or ccw; if several orientations stay consistent with the "
            "facts, reply alternatives.\n\n"
            "Known orientation facts:\n"
        )
        tail = (
            f"\nQueried triple: {q[0]}, {q[1]}, {q[2]}\n"
            "What verdict follows from the stated facts about that triple?"
        )
        return header + "\n".join(lines) + tail

    def score_answer(self, answer, entry):
        try:
            a = answer.strip().lower()
        except Exception:
            return 0.0
        if a == entry.answer:
            return 1.0
        if a not in VALID_INFOS:
            return 0.0
        return 0.0

    def distractor_candidates(self, entry):
        others = sorted(VALID_INFOS - {entry.answer})
        return others
