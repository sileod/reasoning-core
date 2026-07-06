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


def _sample_param(value, value_range, rng):
    return rng.randint(*value_range) if value_range is not None else int(value)


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
    p, u, v = q_consequence
    required = []
    for group in (
        [x for x in q_before if x[0] == p],
        [x for x in q_before if u in x[1:]],
        [x for x in q_before if v in x[1:]],
    ):
        rng.shuffle(group)
        for atom in group:
            if atom not in required:
                required.append(atom)
                break
    near = [x for x in q_before if (x[0] == p or u in x[1:] or v in x[1:]) and x not in required]
    far = [x for x in q_before if x not in near and x not in required]
    rng.shuffle(near)
    rng.shuffle(far)
    return set((required + near + far)[:m])


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


def _hard_negative_case(q_before, q_consequence, m, rng, reverse_rate=0.15):
    case = _inverse_case(q_before, q_consequence, m, rng, reverse_rate=reverse_rate)
    ctx = set(case.context)
    cons = tuple(case.consequence)  # edict coerces the consequence tuple to a list; restore hashability
    nodes, preds = _nodes(ctx | {cons}), _preds(ctx | {cons})
    for atom in rng.sample(list(ctx), len(ctx)):
        p, a, b = atom
        edits = [(p, b, a)]
        edits += [(p, x, b) for x in nodes if x not in (a, b)]
        edits += [(p, a, x) for x in nodes if x not in (a, b)]
        edits += [(q, a, b) for q in preds if q != p]
        rng.shuffle(edits)
        for new_atom in edits:
            if new_atom not in ctx:
                ctx.remove(atom)
                ctx.add(new_atom)
                case.context = ctx
                return case
    return None


def _with_memory_distractors(case, n, rng):
    if n <= 0:
        case.core_context = set(case.context)
        return case

    core = set(case.context)
    cons = tuple(case.consequence)
    nodes = _nodes(core | {cons})
    preds = _preds(core | {cons})

    noise = _rand_atoms(nodes, preds, n, rng, avoid=core | {cons})
    case.core_context = core
    case.context = core | noise
    return case


def _transported_consequences(case, q_before, allow_reverse=True, injective_predicates=True, cap=16):
    c_atoms = set(getattr(case, "core_context", case.context))
    c_cons = tuple(case.consequence)  # edict coerces the consequence tuple to a list; restore hashability
    q_atoms = set(q_before)

    cnodes = _nodes(c_atoms | {c_cons})
    qnodes = _nodes(q_atoms)
    cpreds = _preds(c_atoms | {c_cons})
    qpreds = _preds(q_atoms)

    if len(cnodes) > len(qnodes) or len(cpreds) > len(qpreds):
        return []

    flips = [False, True] if allow_reverse else [False]
    c_order = sorted(c_atoms, key=lambda atom: sum(atom[1:].count(x) for x in cnodes), reverse=True)
    out = set()

    def bind(m, used, a, x):
        if a in m:
            return m if m[a] == x else None
        if x in used:
            return None
        return {**m, a: x}

    def complete_nodes(omap, names):
        missing = [x for x in names if x not in omap]
        pool = [x for x in qnodes if x not in omap.values()]
        for vals in it.permutations(pool, len(missing)):
            yield {**omap, **dict(zip(missing, vals))}

    def search(i, omap, pmap, fmap):
        if len(out) >= cap:
            return
        if i == len(c_order):
            p, a, b = c_cons
            preds = [pmap[p]] if p in pmap else [q for q in qpreds if not injective_predicates or q not in pmap.values()]
            for q in preds:
                for flip in ([fmap[p]] if p in fmap else flips):
                    for omap2 in complete_nodes(omap, [a, b]):
                        x, y = omap2[a], omap2[b]
                        out.add((q, y, x) if flip else (q, x, y))
                        if len(out) >= cap:
                            return
            return

        p, a, b = c_order[i]
        for q, x, y in q_atoms:
            for flip in flips:
                if p in pmap and (pmap[p] != q or fmap[p] != flip):
                    continue
                if p not in pmap and injective_predicates and q in pmap.values():
                    continue
                x, y = (y, x) if flip else (x, y)
                omap2 = bind(omap, set(omap.values()), a, x)
                if omap2 is None:
                    continue
                omap2 = bind(omap2, set(omap2.values()), b, y)
                if omap2 is not None:
                    search(i + 1, omap2, {**pmap, p: q}, {**fmap, p: flip})

    search(0, {}, {}, {})
    return sorted(out)


def _all_consequences(cases, q_before):
    hits = defaultdict(list)
    for case in cases:
        for cons in _transported_consequences(case, q_before):
            hits[cons].append(case.id)
    return hits


def _visible_subset_consequences(case, q_before, min_size=2, max_size=None, cap=64):
    shown = list(case.context)
    max_size = len(shown) if max_size is None else min(max_size, len(shown))
    out = set()

    for r in range(min_size, max_size + 1):
        for sub in it.combinations(shown, r):
            sub = set(sub)
            tmp = edict(context=sub, consequence=case.consequence)
            out.update(_transported_consequences(tmp, q_before, cap=cap))
            if len(out) >= cap:
                return out

    return out


def _case_is_crisp(case, q_before, allowed):
    core = set(getattr(case, "core_context", case.context))
    distractors = set(case.context) - core
    if distractors:
        hits = _visible_subset_consequences(
            edict(context=distractors, consequence=case.consequence),
            q_before,
            min_size=2,
            max_size=len(distractors),
        )
        if not hits <= set(allowed):
            return False

    core_size = len(core)
    hits = _visible_subset_consequences(
        case,
        q_before,
        min_size=core_size,
        max_size=core_size + 1,
    )
    return hits <= set(allowed)


def _crisp_with_memory_distractors(case, n, rng, q_before, allowed, attempts=64):
    if n <= 0:
        return _with_memory_distractors(case, n, rng)

    core = set(getattr(case, "core_context", case.context))
    for _ in range(attempts):
        candidate = edict(context=set(core), consequence=case.consequence)
        candidate = _with_memory_distractors(candidate, n, rng)
        if _case_is_crisp(candidate, q_before, allowed):
            return candidate
    return None


@dataclass
class AnalogicalCaseRetrievalConfig(Config):
    n_query_objects: int = 5
    n_query_links: int = 3
    n_query_facts: int = 6
    n_query_facts_range: tuple | None = None
    n_cases: int = 3
    n_gold_cases: int = 1
    context_facts: int = 4
    memory_distractors: int = 0
    memory_distractors_range: tuple | None = None
    reverse_rate: float = 0.15
    max_attempts: int = 800

    def update(self, c=1):
        self.n_query_objects += c
        self.n_query_facts += 2 * c
        if self.n_query_facts_range is not None:
            lo, hi = self.n_query_facts_range
            self.n_query_facts_range = (lo + 2 * c, hi + 2 * c)
        self.n_cases += c
        self.context_facts += c // 2
        self.reverse_rate = min(0.5, self.reverse_rate + 0.05 * c)

    def apply_difficulty(self, level):
        self.n_query_objects += level
        self.n_query_facts += 2 * level
        if self.n_query_facts_range is not None:
            lo, hi = self.n_query_facts_range
            self.n_query_facts_range = (lo + 2 * level, hi + 2 * level)
        self.n_cases += level
        self.context_facts += 0
        self.reverse_rate = min(0.5, self.reverse_rate + 0.05 * level)


class AnalogicalCaseRetrieval(Task):
    def __init__(self, config=AnalogicalCaseRetrievalConfig()):
        super().__init__(config=config)

    def generate(self):
        k = self.config
        rng = random

        n_obj = int(k.n_query_objects)
        n_rel = int(k.n_query_links)
        n_facts = _sample_param(k.n_query_facts, k.n_query_facts_range, rng)
        n_mem_noise = _sample_param(k.memory_distractors, k.memory_distractors_range, rng)
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

            cases = []
            for _ in range(n_gold):
                case = _crisp_with_memory_distractors(
                    _inverse_case(q_before, q_answer, n_ctx, rng, reverse_rate=k.reverse_rate),
                    n_mem_noise,
                    rng,
                    q_before,
                    {q_answer},
                )
                if case is None:
                    break
                cases.append(case)
            if len(cases) < n_gold:
                continue

            tries = 0
            while len(cases) < n_cases and tries < 800:
                tries += 1
                if rng.random() < 0.75:
                    case = _hard_negative_case(
                        q_before, q_answer, n_ctx, rng, reverse_rate=k.reverse_rate
                    )
                else:
                    case = _random_case(
                        n_nodes=min(n_obj, max(3, len(_nodes(q_before)))),
                        n_preds=n_rel,
                        n_context=n_ctx,
                        rng=rng,
                    )
                if case is None:
                    continue
                case = _crisp_with_memory_distractors(case, n_mem_noise, rng, q_before, set())
                if case is None:
                    continue
                if not _transported_consequences(case, q_before, cap=1):
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
            # ICL framing: answer is the query's consequence (predict-the-relation), not the
            # matching case number. Kept deliberately over the shorter case-number variant — it
            # is a more general in-context-learning task (fills the ICL gap) even though it
            # transfers a bit less. Difficulty is trimmed via the config (fewer cases/facts).
            answer = _sent(q_answer)

            md = edict(
                cases=[
                    edict(
                        id=case.id,
                        context=sorted(case.context),
                        core_context=sorted(getattr(case, "core_context", case.context)),
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
                    memory_distractors=n_mem_noise,
                    reverse_rate=k.reverse_rate,
                ),
            )
            return Problem(metadata=md, answer=answer)

        raise RuntimeError("generation budget exhausted")

    def prompt(self, metadata):
        lines = [
            "Cases show facts that imply one new fact.",
            "Object names and link names may be consistently renamed, and each link name may also have its direction consistently reversed.",
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
        gold = tuple(entry.metadata["answer_atom"])  # edict stores answer_atom as a list; parse yields a tuple
        pred = _parse_sent(answer)
        return 1.0 if pred is not None and tuple(pred) == gold else 0.0
