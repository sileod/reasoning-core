import random
from collections import Counter
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

LABELS = ("greater", "less", "equivalent", "incomparable")


@dataclass
class RecursivePathOrderComparisonConfig(Config):
    nsym: int = 4
    max_depth: int = 2
    comparability: float = 0.7

    def apply_difficulty(self, level):
        self.nsym = 4 + level
        self.max_depth = 2 + level // 2
        self.comparability = 0.7


def _eq(a, b):
    return a == b


def _mul_gt(M, N, higher, ext, memo):
    CM = Counter(M)
    CN = Counter(N)
    if CM == CN:
        return False
    nm = []
    for k, c in CN.items():
        extra = c - CM.get(k, 0)
        for _ in range(extra):
            nm.append(k)
    mn = []
    for k, c in CM.items():
        extra = c - CN.get(k, 0)
        for _ in range(extra):
            mn.append(k)
    for y in nm:
        found = False
        for x in mn:
            if _gt(x, y, higher, ext, memo):
                found = True
                break
        if not found:
            return False
    return True


def _gt(a, b, higher, ext, memo):
    key = (a, b)
    if key in memo:
        return memo[key]
    sa = a[0]
    aa = a[1]
    sb = b[0]
    ab = b[1]
    res = False
    for x in aa:
        if _eq(x, b) or _gt(x, b, higher, ext, memo):
            res = True
            break
    if not res:
        if sb in higher.get(sa, ()):
            ok = True
            for y in ab:
                if not _gt(a, y, higher, ext, memo):
                    ok = False
                    break
            if ok:
                res = True
    if not res and sa == sb:
        if ext == "lex":
            if len(aa) == len(ab):
                for i in range(len(aa)):
                    if not _eq(aa[i], ab[i]):
                        if _gt(aa[i], ab[i], higher, ext, memo):
                            res = True
                        break
        else:
            res = _mul_gt(aa, ab, higher, ext, memo)
    memo[key] = res
    return res


def _compare(a, b, higher, ext):
    memo = {}
    if _eq(a, b):
        return "equivalent"
    if _gt(a, b, higher, ext, memo):
        return "greater"
    if _gt(b, a, higher, ext, memo):
        return "less"
    return "incomparable"


def _build_signature(nsym, comparability):
    nconst = max(2, nsym // 3)
    nfunc = max(2, nsym - nconst)
    consts = ["c%d" % i for i in range(nconst)]
    funcs = ["f%d" % i for i in range(nfunc)]
    arity = {}
    for c in consts:
        arity[c] = 0
    for i, fy in enumerate(funcs):
        arity[fy] = 1 if i == 0 else random.choice([1, 2])
    iso = funcs[-1]
    higher = {s: set() for s in funcs + consts}
    others = funcs[:-1]
    pool = [s for s in funcs + consts if s != iso]
    random.shuffle(pool)
    rank = {s: i for i, s in enumerate(pool)}
    for i in range(len(pool)):
        for j in range(i):
            if random.random() < comparability:
                higher[pool[i]].add(pool[j])

    def _close():
        changed = True
        guard = 0
        while changed and guard < 10000:
            guard += 1
            changed = False
            for s in funcs + consts:
                add = set()
                for h in higher[s]:
                    add.update(higher[h])
                if add - higher[s]:
                    higher[s] |= add
                    changed = True

    _close()

    def _ensure_comparable(x, y):
        if y in higher.get(x, set()) or x in higher.get(y, set()):
            return
        if rank.get(x, -1) > rank.get(y, -1):
            higher[x].add(y)
        else:
            higher[y].add(x)
        _close()

    if len(others) >= 2:
        _ensure_comparable(others[0], others[1])
    if len(consts) >= 2:
        _ensure_comparable(consts[0], consts[1])
    return consts, funcs, arity, higher, iso


def _random_term(arity, depth):
    sym = random.choice(list(arity))
    if arity[sym] == 0 or depth <= 0:
        return (sym, ())
    args = tuple(_random_term(arity, depth - 1) for _ in range(arity[sym]))
    return (sym, args)


def _contrast_pair(higher, ext, arity, others, consts, depth):
    for _ in range(120):
        if random.random() < 0.5 and len(consts) >= 2:
            t1 = (consts[0], ())
            t2 = (consts[1], ())
        else:
            if len(others) >= 2:
                u = others[0]
                v = others[1]
                x = _random_term(arity, max(0, depth - 2))
                t1 = (u, (x,))
                t2 = (v, (x,))
            else:
                continue
        if _gt(t1, t2, higher, ext, {}):
            return t1, t2
    return (consts[0], ()), (consts[1], ())


def _construct(higher, ext, arity, others, consts, iso, depth, target):
    for _ in range(200):
        if target == "equivalent":
            t = _random_term(arity, depth)
            return t, t
        if target == "incomparable":
            fu = iso
            x = _random_term(arity, max(0, depth - 1))
            a = (fu, (x,))
            c = _random_term(arity, depth)
            if _compare(a, c, higher, ext) == "incomparable":
                return a, c
            d = (fu, (x, _random_term(arity, max(0, depth - 1))))
            if arity[fu] > 2:
                pass
            continue
        if target in ("greater", "less"):
            mode = random.random()
            if mode < 0.45 and len(others) >= 2:
                fu, fv = others[0], others[1]
                x = _random_term(arity, max(0, depth - 2))
                a = (fu, (x,))
                b = (fv, (x,))
                if target == "less":
                    a, b = b, a
                if _compare(a, b, higher, ext) == target:
                    return a, b
            elif mode < 0.9:
                f = others[0]
                P = _random_term(arity, max(0, depth - 1))
                c1, c2 = _contrast_pair(higher, ext, arity, others, consts, depth)
                if arity[f] == 2:
                    if target == "greater":
                        a = (f, (P, c1))
                        b = (f, (P, c2))
                    else:
                        a = (f, (P, c2))
                        b = (f, (P, c1))
                    if _compare(a, b, higher, ext) == target:
                        return a, b
            else:
                a = _random_term(arity, depth)
                b = _random_term(arity, depth)
                if _compare(a, b, higher, ext) == target:
                    return a, b
    a = _random_term(arity, depth)
    b = _random_term(arity, depth)
    return a, b


def _render_term(t):
    sym = t[0]
    args = t[1]
    if not args:
        return sym
    return "%s(%s)" % (sym, ",".join(_render_term(x) for x in args))


def _covering(higher, syms):
    covers = []
    for u in syms:
        for v in higher[u]:
            direct = True
            for w in syms:
                if w != u and w != v and v in higher[u] and w in higher[u] and v in higher[w]:
                    direct = False
                    break
            if direct:
                covers.append((u, v))
    return sorted(covers)


class RecursivePathOrderComparison(Task):
    summary = ("Compare two ground term trees under the recursive path ordering, using a "
               "partial symbol precedence and lexicographic or multiset extensions combined "
               "with subterm dominance; determine whether the first term is greater than, "
               "less than, equivalent to, or incomparable with the second.")
    design_choice = ("Kamin-Levy recursive path ordering over a random partial precedence; "
                     "extension mode randomly lexicographic or multiset.")
    config_cls = RecursivePathOrderComparisonConfig

    def generate_entry(self):
        cfg = self.config
        consts, funcs, arity, higher, iso = _build_signature(cfg.nsym, cfg.comparability)
        ext = random.choice(("lex", "mul"))
        target = random.choices(
            LABELS, weights=(0.30, 0.30, 0.20, 0.20)
        )[0]
        others = funcs[:-1]
        a, b = _construct(higher, ext, arity, others, consts, iso, cfg.max_depth, target)
        outcome = _compare(a, b, higher, ext)
        covers = _covering(higher, funcs + consts)
        prec_render = ", ".join("%s > %s" % (u, v) for (u, v) in covers) or "none"
        return Entry(
            metadata={
                "symbols": sorted(funcs + consts),
                "arity": dict(arity),
                "precedence": sorted(
                    ["%s > %s" % (u, v) for u in funcs + consts for v in higher[u]]
                ),
                "covers": covers,
                "ext": ext,
                "A": a,
                "B": b,
                "A_str": _render_term(a),
                "B_str": _render_term(b),
                "answer": outcome,
            },
            answer=outcome,
        )

    def render_prompt(self, metadata):
        order = list(LABELS)
        random.shuffle(order)
        ext_word = "lexicographic" if metadata["ext"] == "lex" else "multiset"
        prec = ", ".join("%s > %s" % (u, v) for (u, v) in metadata["covers"]) or "none"
        opts = ", ".join(order)
        opt_list = ", ".join(order[:-1]) + " or " + order[-1]
        return (
            "Compare the two ground terms A = %s and B = %s under the recursive path "
            "ordering, where the (strict) symbol precedence > is the transitive closure "
            "of: %s. Subterms may dominate as in the standard recursive path ordering, and "
            "terms sharing a root symbol are compared by the %s extension of the ordering "
            "over their argument lists. Is term A greater than, less than, equivalent to, "
            "or incomparable with term B (adjective describing A relative to B)? Answer "
            "with exactly one word from {%s}." % (
                metadata["A_str"], metadata["B_str"], prec, ext_word, opt_list
            )
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        a = answer.strip().lower()
        if a == entry.answer:
            return 1.0
        return 1.0 if a in LABELS and a == entry.answer else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'recursive_path_order_comparison (variant 3 of 3, unguided '
         'baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_relational_structures_r4/recursive_path_order_comparison',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
