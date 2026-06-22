import re, random, itertools as it
from dataclasses import dataclass
from collections import defaultdict
from reasoning_core.template import Task, Problem, Config, edict


LINKS = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "sigma"
]


def _atom(p, a, b):
    return (p, a, b)


def _nodes(atoms):
    return sorted({x for _, a, b in atoms for x in (a, b)})


def _preds(atoms):
    return sorted({p for p, _, _ in atoms})


def _obj_names(n, start=0):
    base = list("abcdefghijklmnopqrstuvwxyz")
    return base[start:start + n] if start + n <= len(base) else [f"o{i}" for i in range(n)]


def _query_names(n):
    base = list("xyzuvw")
    return base[:n] if n <= len(base) else [f"x{i}" for i in range(n)]


def _link_names(n, offset=0):
    return LINKS[offset:offset + n] if offset + n <= len(LINKS) else [f"rel{i}" for i in range(n)]


def _sent(atom):
    p, a, b = atom
    return f"{a} is {p}-linked to {b}."


def _parse_sent(s):
    s = str(s).strip()
    m = re.search(r"\b(\w+)\s+is\s+([A-Za-z]\w*)-linked\s+to\s+(\w+)\b", s)
    if m:
        a, p, b = m.groups()
        return p, a, b
    m = re.search(r"\b([A-Za-z]\w*)\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)", s)
    return m.groups() if m else None


def _rand_atoms(nodes, preds, m, rng, avoid=()):
    avoid = set(avoid)
    pool = [(p, a, b) for p in preds for a in nodes for b in nodes if a != b and (p, a, b) not in avoid]
    rng.shuffle(pool)
    return set(pool[:m])


def _weakly_connected(atoms):
    ns = _nodes(atoms)
    if not ns:
        return False
    adj = defaultdict(set)
    for _, a, b in atoms:
        adj[a].add(b)
        adj[b].add(a)
    seen, stack = {ns[0]}, [ns[0]]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in seen:
                seen.add(v)
                stack.append(v)
    return len(seen) == len(ns)


def _candidate_consequences(before, nodes, preds, rng):
    pool = [(p, a, b) for p in preds for a in nodes for b in nodes if a != b and (p, a, b) not in before]
    rng.shuffle(pool)
    return pool


def _near_context(q_before, q_consequence, m, rng):
    _, u, v = q_consequence
    near = [x for x in q_before if u in x[1:] or v in x[1:]]
    far = [x for x in q_before if x not in near]
    rng.shuffle(near)
    rng.shuffle(far)
    return set((near + far)[:m])


def _inverse_case(q_before, q_consequence, m, rng, reverse_rate=0.15):
    ctx = _near_context(q_before, q_consequence, m, rng)
    all_atoms = sorted(ctx | {q_consequence})
    qnodes, qpreds = _nodes(all_atoms), _preds(all_atoms)

    mnodes = _obj_names(len(qnodes))
    mpreds = _link_names(len(qpreds), 0)
    rng.shuffle(mnodes)
    rng.shuffle(mpreds)

    obj_inv = dict(zip(qnodes, mnodes))
    pred_inv = dict(zip(qpreds, mpreds))
    flip = {p: rng.random() < reverse_rate for p in qpreds}

    def inv(atom):
        p, a, b = atom
        q = pred_inv[p]
        return (q, obj_inv[b], obj_inv[a]) if flip[p] else (q, obj_inv[a], obj_inv[b])

    return edict(context={inv(x) for x in ctx}, consequence=inv(q_consequence))


def _random_case(n_nodes, n_preds, n_context, rng):
    nodes = _obj_names(n_nodes)
    preds = _link_names(n_preds, 0)
    ctx = _rand_atoms(nodes, preds, n_context, rng)
    if not ctx:
        return None
    cons = _candidate_consequences(ctx, nodes, preds, rng)
    if not cons:
        return None
    return edict(context=ctx, consequence=cons[0])


def _transported_consequences(case, q_before, allow_reverse=True, injective_predicates=True, cap=16):
    c_atoms = set(case.context)
    c_cons = case.consequence
    q_atoms = set(q_before)

    cnodes = _nodes(c_atoms | {c_cons})
    qnodes = _nodes(q_atoms)
    cpreds = _preds(c_atoms | {c_cons})
    qpreds = _preds(q_atoms)

    if len(cnodes) > len(qnodes) or len(cpreds) > len(qpreds):
        return []

    flips = [False, True] if allow_reverse else [False]
    out = set()

    for qnode_tuple in it.permutations(qnodes, len(cnodes)):
        omap = dict(zip(cnodes, qnode_tuple))

        for qpred_tuple in it.permutations(qpreds, len(cpreds)):
            pbase = dict(zip(cpreds, qpred_tuple))

            for flip_tuple in it.product(flips, repeat=len(cpreds)):
                fmap = dict(zip(cpreds, flip_tuple))

                ok = True
                for p, a, b in c_atoms:
                    q = pbase[p]
                    x, y = omap[a], omap[b]
                    mapped = (q, y, x) if fmap[p] else (q, x, y)
                    if mapped not in q_atoms:
                        ok = False
                        break
                if not ok:
                    continue

                p, a, b = c_cons
                q = pbase[p]
                x, y = omap[a], omap[b]
                out.add((q, y, x) if fmap[p] else (q, x, y))
                if len(out) >= cap:
                    return sorted(out)

    return sorted(out)


def _all_consequences(cases, q_before):
    hits = defaultdict(list)
    for case in cases:
        for cons in _transported_consequences(case, q_before):
            hits[cons].append(case.id)
    return hits


@dataclass
class AnalogicalCaseRetrievalConfig(Config):
    n_query_objects: int = 5
    n_query_links: int = 3
    n_query_facts: int = 8
    n_cases: int = 6
    n_gold_cases: int = 1
    context_facts: int = 4
    reverse_rate: float = 0.15
    max_attempts: int = 800

    def update(self, c=1):
        self.n_query_objects += c
        self.n_query_facts += 2 * c
        self.n_cases += c
        self.context_facts += c // 2
        self.reverse_rate = min(0.5, self.reverse_rate + 0.05 * c)


class AnalogicalCaseRetrieval(Task):
    def __init__(self, config=AnalogicalCaseRetrievalConfig()):
        super().__init__(config=config)

    def generate(self):
        k = self.config
        rng = random

        n_obj = int(k.n_query_objects)
        n_rel = int(k.n_query_links)
        n_facts = int(k.n_query_facts)
        n_cases = int(k.n_cases)
        n_gold = int(k.n_gold_cases)
        n_ctx = int(k.context_facts)

        qnodes = _query_names(n_obj)
        qpreds = _link_names(n_rel, 2)

        for _ in range(int(k.max_attempts)):
            q_before = _rand_atoms(qnodes, qpreds, n_facts, rng)
            if not _weakly_connected(q_before):
                continue

            consequences = _candidate_consequences(q_before, qnodes, qpreds, rng)
            if not consequences:
                continue
            q_answer = consequences[0]

            cases = [
                _inverse_case(q_before, q_answer, n_ctx, rng, reverse_rate=k.reverse_rate)
                for _ in range(n_gold)
            ]

            tries = 0
            while len(cases) < n_cases and tries < 400:
                tries += 1
                case = _random_case(
                    n_nodes=min(n_obj, max(3, len(_nodes(q_before)))),
                    n_preds=n_rel,
                    n_context=n_ctx,
                    rng=rng,
                )
                if case is None:
                    continue
                if q_answer not in _transported_consequences(case, q_before):
                    cases.append(case)

            if len(cases) < n_cases:
                continue

            rng.shuffle(cases)
            for i, case in enumerate(cases):
                case.id = f"M{i}"

            hits = _all_consequences(cases, q_before)
            if set(hits) != {q_answer}:
                continue

            gold_ids = sorted(hits[q_answer], key=lambda x: int(x[1:]))
            answer = _sent(q_answer)

            md = edict(
                cases=[
                    edict(
                        id=case.id,
                        context=sorted(case.context),
                        consequence=case.consequence,
                    )
                    for case in cases
                ],
                query_context=sorted(q_before),
                answer_atom=q_answer,
                matching_case_ids=gold_ids,
                answer=answer,
                params=dict(
                    n_query_objects=n_obj,
                    n_query_links=n_rel,
                    n_query_facts=n_facts,
                    n_cases=n_cases,
                    n_gold_cases=n_gold,
                    context_facts=n_ctx,
                    reverse_rate=k.reverse_rate,
                ),
            )
            return Problem(metadata=md, answer=answer)

        raise RuntimeError("generation budget exhausted")

    def prompt(self, metadata):
        lines = [
            "Cases show facts that imply one new fact.",
            "Object names and link names may be consistently renamed.",
            "",
        ]

        for case in metadata["cases"]:
            lines.append(case["id"])
            for atom in sorted(case["context"]):
                lines.append(_sent(atom))
            lines.append(f"Implies: {_sent(case['consequence'])}")
            lines.append("")

        lines.append("Query")
        for atom in sorted(metadata["query_context"]):
            lines.append(_sent(atom))
        lines.append("Implies:")

        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.metadata["answer_atom"]
        pred = _parse_sent(answer)
        return 1.0 if pred == gold else 0.0
