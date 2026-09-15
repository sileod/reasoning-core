"""Compose chains of Allen interval relations through their composition table."""

import random
from dataclasses import dataclass
from functools import lru_cache

from reasoning_core.template import Config, Entry, Task

RELATIONS = ("b", "m", "o", "s", "d", "f", "e", "fi", "di", "si", "oi", "mi", "bi")
ORDER = {r: i for i, r in enumerate(RELATIONS)}


def _range_to_rel(a0, a1, b0, b1):
    if a0 >= a1 or b0 >= b1:
        return None
    if a1 < b0:
        return "b"
    if a1 == b0:
        return "m"
    if a0 < b0 and b0 < a1 < b1:
        return "o"
    if a0 == b0 and a1 < b1:
        return "s"
    if a0 < b0 and b1 < a1:
        return "d"
    if a0 < b0 and a1 == b1:
        return "f"
    if a0 == b0 and a1 == b1:
        return "e"
    if b0 < a0 and a1 == b1:
        return "fi"
    if b0 < a0 and a1 < b1:
        return "di"
    if a0 == b0 and b1 < a1:
        return "si"
    if b0 < a0 < b1 and b1 < a1:
        return "oi"
    if a0 == b1:
        return "mi"
    if a0 > b1:
        return "bi"
    return None


@lru_cache(maxsize=None)
def _weak_orderings(items):
    """Ordered set partitions (weak orderings) of a sorted tuple of element names."""
    items = tuple(items)
    if not items:
        return ((),)  # one empty partition
    first = items[0]
    rest = items[1:]
    out = []
    for part in _weak_orderings(rest):
        blocks = [list(b) for b in part]
        for i in range(len(blocks) + 1):
            nb = list(blocks)
            nb.insert(i, [first])
            out.append(tuple(tuple(b) for b in nb))
        for i in range(len(blocks)):
            nb = list(blocks)
            nb[i] = nb[i] + [first]
            out.append(tuple(tuple(b) for b in nb))
    return tuple(out)


def _build_table():
    """Deterministic, complete Allen composition table.

    Enumerate every weak ordering (ordered set partition) of the six endpoints
    {x0,x1,y0,y1,z0,z1}, assigning consecutive ranks within blocks (ties allowed
    within a block). Every real interval configuration induces a weak ordering
    and every weak ordering is realizable, so recording for each pair
    (rel X-Y, rel Y-Z) every rel X-Z found is a complete construction: every
    nonempty composition cell is hit exactly. All 169 cells are verified present.
    """
    table = {}
    endpoints = ("x0", "x1", "y0", "y1", "z0", "z1")
    for part in _weak_orderings(endpoints):
        val = {}
        for rank, block in enumerate(part):
            for name in block:
                val[name] = rank
        x0, x1, y0, y1, z0, z1 = (val[k] for k in endpoints)
        ra = _range_to_rel(x0, x1, y0, y1)
        rb = _range_to_rel(y0, y1, z0, z1)
        rc = _range_to_rel(x0, x1, z0, z1)
        if ra is None or rb is None or rc is None:
            continue
        table.setdefault((ra, rb), set()).add(rc)
    for ra in RELATIONS:
        for rb in RELATIONS:
            cell = table.get((ra, rb))
            if not cell:
                raise RuntimeError(f"missing composition cell {ra},{rb}")
    return {k: frozenset(v) for k, v in table.items()}


TABLE = _build_table()


def _compose_step(symbols_a, symbols_b):
    out = set()
    for a in symbols_a:
        for b in symbols_b:
            out |= TABLE[(a, b)]
    return frozenset(sorted(out))


def compose_chain(chain):
    """chain: list of frozensets of relation symbols. Returns list sorted in the
    canonical ORDER (b,m,o,s,d,f,e,fi,di,si,oi,mi,bi)."""
    out = chain[0]
    for i in range(1, len(chain)):
        out = _compose_step(out, chain[i])
    return sorted(out, key=ORDER.__getitem__)


class AllenIntervalCompositionV1Config(Config):
    n_steps: int = 2
    max_disj: int = 2

    def apply_difficulty(self, level):
        self.n_steps = min(4, 2 + level // 2)
        self.max_disj = 2


class AllenIntervalComposition(Task):
    summary = "Compose chains of Allen interval relations, with disjunctions and inverses, through the standard composition table; return the tightest entailed relation set between the chain's endpoints."
    design_choice = "Present each instance as a triple of Allen relations with one disjunction per step and ask for the composed relation set as a canonical comma-separated list of relation symbols."
    config_cls = AllenIntervalCompositionV1Config
    task_version = 2

    def generate_entry(self):
        n_steps = self.config.n_steps
        max_disj = self.config.max_disj
        full_set = set(RELATIONS)
        attempts = 0
        while True:
            attempts += 1
            if attempts > 200:
                raise RuntimeError("could not find a non-full composition")
            chain = []
            for _ in range(n_steps):
                k = random.randint(2, max_disj)
                disj = frozenset(random.sample(RELATIONS, k))
                chain.append(disj)
            ans = compose_chain(chain)
            if not ans:
                continue
            # Skip the trivial full-set answer so the distribution stays varied
            # and informative; partial entailed sets are the interesting case.
            if set(ans) == full_set:
                continue
            break
        return Entry(
            metadata={
                "chain": [sorted(s) for s in chain],
                "answer_set": ans,
            },
            answer=",".join(ans),
        )

    def render_prompt(self, metadata):
        chain = metadata["chain"]
        parts = []
        for i, s in enumerate(chain, start=1):
            parts.append(" ".join(s))
        chain_txt = " && ".join(parts)
        return (
            "An interval X relates to an interval Y by one of the thirteen Allen "
            "relations, written b m o s d f e fi di si oi mi bi. For consecutive "
            "intervals X, Y, Z the Allen composition table maps each ordered pair "
            "of relations (r,s) to Comp(r,s), the set of possible relations "
            "between X and Z when X r Y and Y s Z. Steps that list several "
            "relations joined by '&&' are disjunctions (the step holds if at "
            "least one listed relation holds). Compose the following chain of "
            f"disjunctions left to right using the composition table:\n\n"
            f"{chain_txt}\n\n"
            "Report the tightest relation set entailed between the first and last "
            "interval of the chain: the union over every consistent choice of one "
            "relation per step, of the relations allowed by repeated composition. "
            "Give the answer as a comma-separated list of relation symbols in the "
            "fixed order b,m,o,s,d,f,e,fi,di,si,oi,mi,bi, keeping only relations "
            "that are possible. Answer only the list, e.g. 'o,s'."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        parsed = [t.strip() for t in answer.split(",")]
        if not parsed or any(t == "" for t in parsed):
            return 0.0
        if len(set(parsed)) != len(parsed):
            return 0.0
        try:
            idx = [ORDER[p] for p in parsed]
        except KeyError:
            return 0.0
        if idx != sorted(idx):
            return 0.0
        gold = set(entry.metadata["answer_set"])
        if set(parsed) != gold:
            return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'allen_interval_composition (draw 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/allen_interval_composition',
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
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
