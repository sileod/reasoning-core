import random
from dataclasses import dataclass
from datetime import date, timedelta

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'bitemporal_correction_slicing (variant 1 of 3)',
 'hypothesis': 'P010',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_incremental_recomputation_r4/bitemporal_correction_slicing',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2409743872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_BASE = date(2024, 1, 1)
_TZ = date(2024, 7, 1)
_FRONTIER = date(2024, 12, 31)
_ALPHABET = "0123"


def _d(offset):
    return _BASE + timedelta(days=offset)


def _fmt(d):
    return d.isoformat()


def _maximal_changed(segs, cv_start, cv_end, new_val):
    pre = {}
    for vs, ve, val in segs:
        for d in range(vs, ve):
            pre[d] = val
    changed = [d for d in range(cv_start, cv_end) if pre[d] != new_val]
    out = []
    if not changed:
        return out
    s = e = changed[0]
    for d in changed[1:]:
        if d == e + 1:
            e = d
        else:
            out.append((s, e + 1))
            s = e = d
    out.append((s, e + 1))
    return out


@dataclass
class BitemporalCorrectionSlicingConfig(Config):
    nseg: int = 2
    horizon: int = 90
    min_gap: int = 8
    max_span: int = 25

    def apply_difficulty(self, level):
        self.nseg = 2 + level
        self.horizon = 90 + 40 * level
        self.min_gap = 8 + 4 * level
        self.max_span = 25 + 15 * level


class BitemporalCorrectionSlicing(Task):
    summary = ("Apply a retroactive interval correction to a bitemporal record's valid-time "
               "partition at a stated transaction time; split the affected valid-time region "
               "against segment boundaries, preserving earlier as-of views, and return the "
               "maximal valid x transaction changed-history rectangles.")
    design_choice = ("Answer form is a compact list of changed intervals in ISO 8601 with 'V'/'T' "
                     "prefixes and ';' separators, e.g. '[V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]'")
    config_cls = BitemporalCorrectionSlicingConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        horizon, nseg, min_gap, max_span = cfg.horizon, cfg.nseg, cfg.min_gap, cfg.max_span

        while True:
            breakpoints = sorted(random.sample(range(1, horizon), nseg - 1))
            bounds = [0] + breakpoints + [horizon]
            if min(bounds[i + 1] - bounds[i] for i in range(nseg)) < min_gap:
                continue
            vals = [random.choice(list(_ALPHABET)) for _ in range(nseg)]

            b = random.randrange(0, nseg - 1)
            b2 = random.randint(b + 1, nseg - 1)
            if vals[b] == vals[b2]:
                vals[b2] = random.choice([c for c in _ALPHABET if c != vals[b]])
            new_val = vals[b]
            if random.random() < 0.5 and b2 >= b + 2:
                hole = random.randint(b + 1, b2 - 1)
                vals[hole] = new_val
            s_lo, s_hi = bounds[b], bounds[b + 1]
            e_lo, e_hi = bounds[b2], bounds[b2 + 1]
            cv_start = random.randint(s_lo, s_hi - 1)
            cv_end = random.randint(e_lo + 1, e_hi)
            if cv_end - cv_start > max_span:
                cv_end = cv_start + max_span
                if cv_end > e_hi:
                    cv_end = e_hi
            if cv_end <= cv_start:
                continue

            segs = [(bounds[i], bounds[i + 1], vals[i]) for i in range(nseg)]
            changed = _maximal_changed(segs, cv_start, cv_end, new_val)
            if not changed:
                continue

            seg_meta = [
                {"valid_from": _fmt(_d(vs)), "valid_to": _fmt(_d(ve)), "value": val}
                for vs, ve, val in segs
            ]
            metadata = {
                "segments": seg_meta,
                "cv_start": _fmt(_d(cv_start)),
                "cv_end": _fmt(_d(cv_end)),
                "new_value": new_val,
                "tz": _fmt(_TZ),
                "frontier": _fmt(_FRONTIER),
                "changed_offsets": [[vs, ve] for vs, ve in changed],
            }
            parts = [
                "V{}/{},T{}/{}".format(_fmt(_d(vs)), _fmt(_d(ve)), _fmt(_TZ), _fmt(_FRONTIER))
                for vs, ve in changed
            ]
            answer = "[" + ";".join(parts) + "]"
            return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        seg_lines = "\n".join(
            "- [{} to {}, value {}]".format(s["valid_from"], s["valid_to"], s["value"])
            for s in metadata["segments"]
        )
        return (
            "A bitemporal record stores history as (valid_from, valid_to) segments, each with a "
            "single value still in force over the transaction interval {} to {} (until further "
            "notice). Its current valid-time partition is:\n{}\n"
            "At transaction time {} a retroactive correction is applied: the record's value "
            "becomes {} over the valid-time interval [{} to {}). Slicing the affected valid-time "
            "region against the existing segment boundaries (earlier as-of views are preserved; "
            "only the currently-in-force layer changes).\n"
            "Return the changed history rectangles: every maximal valid-time interval inside "
            "[{} to {}) whose value changes from its previous value to {}, expressed as rectangles "
            "in the format [V<valid_from>/<valid_to>,T<tz>/<frontier>], sorted ascending by "
            "valid_from and joined with ';'. Here tz={} and frontier={}.\n"
            "Format example: [V2024-01-01/2024-03-01,T2024-06-01/2024-06-15]"
        ).format(
            metadata["tz"], metadata["frontier"],
            seg_lines,
            metadata["tz"],
            metadata["new_value"],
            metadata["cv_start"], metadata["cv_end"],
            metadata["cv_start"], metadata["cv_end"], metadata["new_value"],
            metadata["tz"], metadata["frontier"],
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        ref = entry["answer"]
        a = str(answer).strip()
        r = str(ref).strip()
        return 1.0 if a == r else 0.0
