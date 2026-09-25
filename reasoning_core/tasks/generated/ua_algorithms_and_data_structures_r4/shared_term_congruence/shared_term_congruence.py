import random
from dataclasses import dataclass

from reasoning_core.template import Entry, Config, Task, edict


@dataclass
class SharedTermConfig(Config):
    n_constants: int = 5
    n_link: int = 2
    n_queries: int = 4
    depth: int = 1
    n_binary: int = 2
    n_unary: int = 2

    def apply_difficulty(self, level):
        self.n_constants = int(4 + 0.6 * level)
        self.n_link = int(1 + 0.4 * level)
        self.n_queries = int(4 + 0.7 * level)
        if self.n_queries % 2:
            self.n_queries += 1
        self.depth = int(1 + 0.35 * level)
        self.n_binary = 2
        self.n_unary = 2


_SYM = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n"]
_UNARY_OPS = ["p", "f", "g"]
_BINARY_OPS = ["h", "k", "m"]


def _children(term):
    return term[1] if isinstance(term, tuple) else ()


def _congruence(terms, equalities):
    parent = {}

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            nxt = parent[x]
            parent[x] = root
            x = nxt
        return root

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    allnodes = set()

    def collect(t):
        allnodes.add(t)
        for c in _children(t):
            collect(c)

    for t in terms:
        collect(t)
    for n in allnodes:
        parent[n] = n
    for (a, b) in equalities:
        union(a, b)
    changed = True
    while changed:
        changed = False
        sig = {}
        for t in sorted(allnodes, key=repr):
            if isinstance(t, tuple):
                key = (t[0], tuple(find(c) for c in t[1]))
                if key in sig:
                    if find(sig[key]) != find(t):
                        union(sig[key], t)
                        changed = True
                else:
                    sig[key] = t
    return {n: find(n) for n in allnodes}


def _ts(term):
    if isinstance(term, tuple):
        return term[0] + "(" + ",".join(_ts(c) for c in term[1]) + ")"
    return term


class SharedTermCongruence(Task):
    summary = ("Propagate asserted equalities through shared term structures: constants are "
               "merged by direct assertion while unary and binary function terms merge only "
               "when their operators and every corresponding child class coincide, yielding "
               "forced-equal and forced-different query answers across nested shared sub-terms; "
               "answers are a canonical T/F string, one boolean per query pair.")
    design_choice = ("Instances present a list of equality assertions and a fixed set of query "
                     "pairs; the answer is a canonical list of true/false booleans for each pair.")
    config_cls = SharedTermConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        for _ in range(500):
            constants = _SYM[: cfg.n_constants]
            random.shuffle(constants)
            n_link = cfg.n_link
            pairs = []
            for i in range(n_link):
                pairs.append((constants[2 * i], constants[2 * i + 1]))
            singleton = constants[2 * n_link:]
            unary = random.sample(_UNARY_OPS, min(cfg.n_unary, len(_UNARY_OPS)))
            binary = random.sample(_BINARY_OPS, min(cfg.n_binary, len(_BINARY_OPS)))

            equalities = [pair for pair in pairs]

            terms = list(constants)

            def note(t):
                terms.append(t)

            queries = []
            half = cfg.n_queries // 2
            true_q = []
            false_q = []

            for (x, y) in pairs:
                for L in range(1, cfg.depth + 1):
                    seq = [random.choice(unary) for _ in range(L)]
                    wx = x
                    wy = y
                    for op in seq:
                        wx = (op, (wx,))
                        wy = (op, (wy,))
                    note(wx)
                    note(wy)
                    true_q.append((wx, wy))
                if binary:
                    filler = random.choice(constants)
                    for op in binary:
                        left = (op, (x, filler))
                        right = (op, (y, filler))
                        note(left)
                        note(right)
                        true_q.append((left, right))

            if len(pairs) > 1 and binary:
                (x, y) = pairs[0]
                for i in range(1, len(pairs)):
                    (u, v) = pairs[i]
                    for op in binary:
                        left = (op, (x, u))
                        right = (op, (y, v))
                        note(left)
                        note(right)
                        true_q.append((left, right))

            reps = [p[0] for p in pairs] + list(singleton)
            classes = list(range(len(pairs))) + [len(pairs) + i
                                                 for i in range(len(singleton))]
            for i in range(len(reps)):
                for j in range(i + 1, len(reps)):
                    if classes[i] == classes[j]:
                        continue
                    r1, r2 = reps[i], reps[j]
                    false_q.append((r1, r2))
                    for L in range(1, cfg.depth + 1):
                        seq = [random.choice(unary) for _ in range(L)]
                        w1, w2 = r1, r2
                        for op in seq:
                            w1 = (op, (w1,))
                            w2 = (op, (w2,))
                        note(w1)
                        note(w2)
                        false_q.append((w1, w2))
                    if binary and len(reps) > 2:
                        r3 = reps[(j + 1) % len(reps)]
                        if classes[(j + 1) % len(reps)] != classes[i]:
                            fb = (binary[0], (r1, r2))
                            fb2 = (binary[0], (r3, r2))
                            note(fb)
                            note(fb2)
                            false_q.append((fb, fb2))

            random.shuffle(true_q)
            random.shuffle(false_q)

            if len(true_q) < half or len(false_q) < half:
                continue
            sel_true = true_q[:half]
            sel_false = false_q[:half]
            queries = sel_true + sel_false
            labels = [True] * half + [False] * half
            order = list(range(len(queries)))
            random.shuffle(order)
            queries = [queries[i] for i in order]
            labels = [labels[i] for i in order]

            cl = _congruence(terms + [a for (a, b) in queries] + [b for (a, b) in queries],
                             equalities)
            ok = True
            for (a, b), want in zip(queries, labels):
                if (cl[a] == cl[b]) != want:
                    ok = False
                    break
            if not ok:
                continue
            answer = "".join("T" if b else "F" for b in labels)
            if "T" not in answer or "F" not in answer:
                continue
            metadata = dict(
                constants=constants,
                pairs=[list(p) for p in pairs],
                singleton=singleton,
                unary_ops=unary,
                binary_ops=binary,
                equalities=[list(e) for e in equalities],
                queries=[list(q) for q in queries],
                labels=labels,
                depth=cfg.depth,
            )
            return Entry(metadata=edict(metadata), answer=answer)
        raise RuntimeError("failed to generate a valid shared-term-congruence instance")

    def render_prompt(self, metadata):
        m = metadata
        ops = " ".join(f"{op}/{1}" for op in m["unary_ops"]) + " " + \
              " ".join(f"{op}/{2}" for op in m["binary_ops"])
        eqs = "; ".join(f"{_ts(a)} == {_ts(b)}" for (a, b) in m["equalities"])
        qps = "; ".join(f"({_ts(a)}, {_ts(b)})" for (a, b) in m["queries"])
        prompt = (
            "We reason about terms built from constant symbols %s and operator symbols "
            "%s, where each operator is applied to a fixed number of child terms "
            "(unary/binary as shown). Two terms are considered equal if they can be "
            "derived from the following given equalities by congruence closure: "
            "constants merge only when an equality says they merge, and two function "
            "terms f(c1,...,cn) and g(d1,...,dm) merge exactly when f == g, n == m, and "
            "every corresponding child ci merges with di. Given equalities: %s. "
            "Decide, for each query pair, whether congruence closure forces the two "
            "terms to be equal. Query pairs (term1, term2): %s. "
            "Answer with one T (forced equal) or F (not forced) per query pair, in the "
            "order given, written as a single string of T/F characters (e.g. TFTF)."
        ) % (", ".join(m["constants"]), ops, eqs, qps)
        return prompt

    def score_answer(self, answer, entry):
        return float(_norm(answer) == _norm(entry.answer))


def _norm(text):
    return "".join(str(text).replace(",", " ").split()).upper()


TASK_META = {'parent_source_id': None,
 'idea': 'shared_term_congruence (variant 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_algorithms_and_data_structures_r4/shared_term_congruence',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
