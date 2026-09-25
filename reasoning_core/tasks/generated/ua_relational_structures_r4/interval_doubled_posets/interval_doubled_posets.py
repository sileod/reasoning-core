import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class IntervalDoubledPosetsV2Config(Config):
    n_base: int = 4
    n_double: int = 2
    max_elems: int = 16

    def apply_difficulty(self, level):
        self.n_base = stochastic_rounding(3 + level)
        self.n_double = stochastic_rounding(2 + level * 2 // 3)
        self.max_elems = 16 + 2 * level


def _closure(le):
    m = len(le)
    reach = [set(s) for s in le]
    changed = True
    while changed:
        changed = False
        for i in range(m):
            for j in list(reach[i]):
                add = reach[j] - reach[i]
                if add:
                    reach[i] |= add
                    changed = True
    return reach


def _covers(le):
    m = len(le)
    out = []
    for j in range(m):
        cands = sorted(i for i in range(m) if i != j and j in le[i])
        for i in cands:
            between = [
                k
                for k in range(m)
                if k != i and k != j and j in le[k] and k in le[i]
            ]
            if not between:
                out.append((i, j))
    return out


def _addr_str(t):
    return ".".join(str(x) for x in t)


def _build_doubled(addr, le, I):
    m = len(addr)
    inI = [False] * m
    for x in I:
        inI[x] = True
    newaddr = []
    mapidx = {}
    for x in range(m):
        if inI[x]:
            mapidx[(x, 0)] = len(newaddr)
            newaddr.append(addr[x] + (0,))
            mapidx[(x, 1)] = len(newaddr)
            newaddr.append(addr[x] + (1,))
        else:
            mapidx[x] = len(newaddr)
            newaddr.append(addr[x])
    M = len(newaddr)
    le2 = [set([i]) for i in range(M)]
    for x in range(m):
        for y in le[x]:
            xin, yin = inI[x], inI[y]
            if not xin and not yin:
                le2[mapidx[x]].add(mapidx[y])
            elif xin and not yin:
                le2[mapidx[(x, 0)]].add(mapidx[y])
                le2[mapidx[(x, 1)]].add(mapidx[y])
            elif not xin and yin:
                le2[mapidx[x]].add(mapidx[(y, 0)])
                le2[mapidx[x]].add(mapidx[(y, 1)])
            else:
                le2[mapidx[(x, 0)]].add(mapidx[(y, 0)])
                le2[mapidx[(x, 0)]].add(mapidx[(y, 1)])
                le2[mapidx[(x, 1)]].add(mapidx[(y, 1)])
                if x != y:
                    le2[mapidx[(x, 1)]].add(mapidx[(y, 0)])
    return newaddr, _closure(le2)


def _build_base(n):
    le = [set([i]) for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if random.random() < 0.5:
                le[i].add(j)
    addr = [(i,) for i in range(n)]
    return addr, _closure(le)


def _generate(cfg):
    n = cfg.n_base
    for _attempt in range(300):
        addr, le = _build_base(n)
        base_covers = _covers(le)
        doublings = []
        ok = True
        for _step in range(cfg.n_double):
            m = len(addr)
            cmp = [
                (i, j)
                for i in range(m)
                for j in range(m)
                if i != j and j in le[i]
            ]
            if not cmp:
                ok = False
                break
            chosen = None
            for _t in range(60):
                lo, hi = random.choice(cmp)
                I = [x for x in range(m) if x in le[lo] and hi in le[x]]
                newcount = (m - len(I)) + 2 * len(I)
                if newcount <= cfg.max_elems:
                    chosen = (lo, hi, I)
                    break
            if chosen is None:
                ok = False
                break
            lo, hi, I = chosen
            doublings.append([_addr_str(addr[lo]), _addr_str(addr[hi])])
            addr, le = _build_doubled(addr, le, I)
        if not ok:
            continue
        m = len(addr)
        cov_pairs = _covers(le)
        cmp = [
            (i, j)
            for i in range(m)
            for j in range(m)
            if i != j and j in le[i]
        ]
        covset = set(cov_pairs)
        noncov = [(i, j) for (i, j) in cmp if (i, j) not in covset]
        if not (cov_pairs and noncov):
            continue
        if random.random() < 0.5:
            i, j = random.choice(cov_pairs)
            answer = "YES"
        else:
            i, j = random.choice(noncov)
            answer = "NO"
        a = _addr_str(addr[i])
        b = _addr_str(addr[j])
        return {
            "base_covers": [[int(x), int(y)] for (x, y) in base_covers],
            "n_base": int(n),
            "doublings": doublings,
            "cmp": [_addr_str(addr[x]) for x in (i, j)],
            "answer": answer,
        }
    raise RuntimeError("could not generate an interval-doubled poset instance")


def _render_rule():
    return (
        "A doubling of an interval [a,b] (the set of all t with a<=t<=b) replaces every "
        "t in the interval by a lower copy t' and an upper copy t'', ordered t'<t''. "
        "Elements outside the interval keep their identity. Order between copies: for "
        "originals u<=v inside the interval we put u'<=v', u'<=v'' and u''<=v''; "
        "additionally u''<=v' holds only when u<v strictly (so the two layers stay "
        "distinct). An element o outside the interval satisfies o<=t-copy iff o<=t, and "
        "t-copy<=o iff t<=o."
    )


class IntervalDoubledPosets(Task):
    summary = (
        "Replace selected intervals of finite posets by ordered two-layer copies while "
        "inheriting outside comparisons; compose overlapping doublings and answer "
        "comparability or cover queries between resulting elements."
    )
    config_cls = IntervalDoubledPosetsV2Config
    design_choice = (
        "Doublings are applied sequentially with intervals chosen from the current "
        "poset, and the answer is a canonical cover relation (cover or not) between two "
        "elements, using a fixed element-labeling scheme."
    )

    def generate_entry(self):
        data = _generate(self.config)
        return Entry(metadata=data, answer=data["answer"])

    def render_prompt(self, metadata):
        n = metadata["n_base"]
        base = " ".join(f"({a},{b})" for (a, b) in metadata["base_covers"])
        if not base:
            base = "(none)"
        intro = (
            f"Consider a finite poset (partially ordered set) whose elements are named "
            f"0,1,...,{n-1} and whose cover relations (immediate orderings, a direct "
            f"successor of b when a<b and no element lies strictly between) are: {base}. "
            f"Here a<b means the reflexive-transitive closure, and elements are "
            f"comparable when one is below the other in that closure."
        )
        rule = _render_rule()
        dbl = "; ".join(
            f"double the interval [{a}, {b}] of the current poset" for (a, b) in metadata["doublings"]
        )
        (x, y) = metadata["cmp"]
        return (
            intro + " " + rule + " Apply the following doublings in order, each to the "
            "current poset (intervals are named by the current element identities): "
            + dbl + ". After all doublings, consider the element " + x + " and the "
            "element " + y + ". Does the element " + y + " directly cover the element "
            + x + " (i.e. x<y and no element lies strictly between them in the final "
            "poset)? Reply exactly YES or NO. The compared elements are " + x + " and "
            + y + "."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip().upper() == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'interval_doubled_posets (variant 2 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/interval_doubled_posets',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
