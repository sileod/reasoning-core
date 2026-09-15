import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

_FUNS = list("ABCDEGHJKLMNPQRSTUVWXYZ")
_CONSTS = [0, 1, 2, 3]
_CTX_VARS = ["c", "d", "e", "f", "g", "k"]
_X_VARS = ["x", "y", "z", "u", "v"]
_SIG_VARS = ["m", "n", "p", "q", "r"]

TASK_META = {'parent_source_id': None,
 'idea': 'critical_pair_generation (draw 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_representation_transfer_r1/critical_pair_generation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}


def render(node):
    t = node[0]
    if t == "var":
        return node[1]
    if t == "const":
        return str(node[1])
    return node[1] + "(" + ",".join(render(ch) for ch in node[2]) + ")"


def _parse(toks, pos):
    tok = toks[pos]
    if pos + 1 < len(toks) and toks[pos + 1] == "(":
        name, args, k = tok, [], pos + 2
        while True:
            node, k = _parse(toks, k)
            args.append(node)
            if toks[k] == ",":
                k += 1
            elif toks[k] == ")":
                return ("fun", name, args), k + 1
            else:
                raise ValueError("bad term")
    else:
        if tok.isdigit():
            return ("const", int(tok)), pos + 1
        return ("var", tok), pos + 1


def parse(text):
    toks = [t for t in text if t not in " \t"]
    node, k = _parse(toks, 0)
    return node


def gather_vars(node):
    out = []
    stack = [node]
    while stack:
        x = stack.pop()
        if x[0] == "var":
            out.append(x[1])
        elif x[0] == "fun":
            stack.extend(x[2])
    return sorted(set(out))


def gather_heads(node):
    out = []
    stack = [node]
    while stack:
        x = stack.pop()
        if x[0] == "fun":
            out.append(x[1])
            stack.extend(x[2])
    return out


def subterm_at(node, path):
    for i in path:
        node = node[2][i]
    return node


def replace_at(node, path, rep):
    if not path:
        return rep
    i = path[0]
    children = list(node[2])
    children[i] = replace_at(children[i], path[1:], rep)
    return ("fun", node[1], children)


def apply_subst(node, subst):
    t = node[0]
    if t == "var":
        return subst.get(node[1], node)
    if t == "fun":
        return ("fun", node[1], [apply_subst(ch, subst) for ch in node[2]])
    return node


def _resolve(t, subst):
    while t[0] == "var" and t[1] in subst:
        t = subst[t[1]]
    return t


def _occurs(v, t, subst):
    t = _resolve(t, subst)
    if t[0] == "var":
        return t[1] == v
    if t[0] == "fun":
        return any(_occurs(v, ch, subst) for ch in t[2])
    return False


def unify(a, b, subst):
    a = _resolve(a, subst)
    b = _resolve(b, subst)
    if a[0] == "var":
        if a == b:
            return True
        if _occurs(a[1], b, subst):
            return False
        subst[a[1]] = b
        return True
    if b[0] == "var":
        return unify(b, a, subst)
    if a[0] == "const" or b[0] == "const":
        return a == b
    if a[1] != b[1] or len(a[2]) != len(b[2]):
        return False
    for ca, cb in zip(a[2], b[2]):
        if not unify(ca, cb, subst):
            return False
    return True


def gen_structure(depth, pool, max_arity, vars_):
    if depth <= 0 or (vars_ and random.random() < 0.35):
        if vars_ and random.random() < 0.55:
            return ("var", random.choice(vars_))
        return ("const", random.choice(_CONSTS))
    name = random.choice(pool)
    ar = random.randint(1, max_arity)
    return ("fun", name, [gen_structure(depth - 1, pool, max_arity, vars_)
                          for _ in range(ar)])


def gen_pattern(depth, max_arity, vars_):
    if depth <= 0 or random.random() < 0.45:
        return ("var", random.choice(vars_))
    name = random.choice(_FUNS)
    ar = random.randint(1, max_arity)
    return ("fun", name, [gen_pattern(depth - 1, max_arity, vars_)
                          for _ in range(ar)])


def build_context_around(path, s, pool, max_arity, leaf_depth):
    if not path:
        return s
    head = path[0]
    ar = head + 1 + random.randint(0, max(0, max_arity - (head + 1)))

    def subtree(i):
        if i == head:
            return build_context_around(path[1:], s, pool, max_arity, leaf_depth)
        if random.random() < 0.5:
            return ("var", random.choice(_CTX_VARS))
        return gen_structure(leaf_depth, pool, max_arity, _CTX_VARS)

    return ("fun", random.choice(pool), [subtree(i) for i in range(ar)])


@dataclass
class CriticalPairConfig(Config):
    frac_overlap: float = 0.7
    ctx_depth: int = 2
    tdepth: int = 1
    max_arity: int = 2
    rule_depth: int = 1

    def apply_difficulty(self, level):
        self.frac_overlap = 0.7
        self.ctx_depth = 2 + level // 2
        self.tdepth = 1 + level // 2
        self.rule_depth = 1 + level // 2
        self.max_arity = 2 if level < 4 else 3


class CriticalPairGeneration(Task):
    summary = ("Unify the left-hand side of one rewrite rule into a non-variable "
               "subterm of another, apply the mated substitution to both right-hand "
               "sides, and return the directed critical pair of terms or an empty "
               "result when no overlap exists.")
    design_choice = ("Represent terms as fully parenthesized prefix strings with "
                     "explicit variable names, and return the two rewritten terms "
                     "separated by a semicolon, or 'NONE' when no overlap.")
    config_cls = CriticalPairConfig

    task_version = 2

    def generate_entry(self):
        level = getattr(self.config, "level", 0)
        c = self.config
        bh = random.choice(_FUNS)
        pool = [f for f in _FUNS if f != bh]

        X = [random.choice(_X_VARS) for _ in range(random.randint(1, 3))]
        xvars = sorted(set(X))
        ar_b = random.randint(1, c.max_arity)
        lhs_b = ("fun", bh, [gen_pattern(c.rule_depth, c.max_arity, xvars)
                             for _ in range(ar_b)])
        sigma_terms = {v: gen_structure(c.tdepth, pool, c.max_arity, _SIG_VARS)
                       for v in xvars}
        s = apply_subst(lhs_b, sigma_terms)

        if random.random() < c.frac_overlap:
            plen = random.randint(1, c.ctx_depth)
            path = [random.randint(0, 1) for _ in range(plen)]
            lhs_a = build_context_around(path, s, pool, c.max_arity, c.tdepth)

            rhs_vars = sorted(set(gather_vars(lhs_a)) | set(_SIG_VARS))
            rhs_b = gen_structure(c.tdepth, pool, c.max_arity, xvars)
            rhs_a = gen_structure(c.tdepth, pool, c.max_arity, rhs_vars)

            sub = subterm_at(lhs_a, path)
            mgu = {}
            if not unify(lhs_b, sub, mgu):
                raise RuntimeError("constructed overlap failed to unify")
            if sub[0] != "fun":
                raise RuntimeError("overlap subterm is not non-variable")

            r1sig = apply_subst(rhs_a, mgu)
            r2sig = apply_subst(rhs_b, mgu)
            lhs_a_sig = apply_subst(lhs_a, mgu)
            rewritten = replace_at(lhs_a_sig, path, r2sig)
            answer = render(r1sig) + " ; " + render(rewritten)

            if unify(lhs_b, s, {}) is False:
                raise RuntimeError
            if render(replace_at(lhs_a_sig, path, r2sig)) != render(rewritten):
                raise RuntimeError

            metadata = {
                "a_lhs": render(lhs_a), "a_rhs": render(rhs_a),
                "b_lhs": render(lhs_b), "b_rhs": render(rhs_b),
                "head_symbol": bh, "overlap": True, "path": path,
                "sigma": ";".join(sorted(f"{k}->{render(t)}"
                                         for k, t in mgu.items())),
            }
            return Entry(metadata=metadata, answer=answer)
        else:
            plen = random.randint(1, c.ctx_depth)
            path = [random.randint(0, 1) for _ in range(plen)]
            dud = gen_structure(c.tdepth, pool, c.max_arity, _SIG_VARS)
            lhs_a = build_context_around(path, dud, pool, c.max_arity, c.tdepth)
            if bh in gather_heads(lhs_a):
                raise RuntimeError("unexpected head symbols")
            rhs_vars = sorted(set(gather_vars(lhs_a)) | set(_SIG_VARS))
            rhs_b = gen_structure(c.tdepth, pool, c.max_arity, xvars)
            rhs_a = gen_structure(c.tdepth, pool, c.max_arity, rhs_vars)
            metadata = {
                "a_lhs": render(lhs_a), "a_rhs": render(rhs_a),
                "b_lhs": render(lhs_b), "b_rhs": render(rhs_b),
                "head_symbol": bh, "overlap": False, "path": path,
                "sigma": "",
            }
            return Entry(metadata=metadata, answer="NONE")

    def render_prompt(self, metadata):
        block = (f"Two rewrite rules over first-order terms are given in prefix "
                 f"notation.\n  A: {metadata['a_lhs']} -> {metadata['a_rhs']}\n"
                 f"  B: {metadata['b_lhs']} -> {metadata['b_rhs']}\n"
                 f"Form the critical pair by overlapping rule B into a proper "
                 f"(non-root) subterm of rule A's left-hand side: the unique "
                 f"occurrence in A's left-hand side whose head function symbol "
                 f"is {metadata['head_symbol']}. Unify that subterm with B's "
                 f"left-hand side to obtain the most general unifier, apply it "
                 f"to both right-hand sides, and rewrite A's left-hand side at "
                 f"the overlap with rule B. If B's left-hand side overlaps no "
                 f"proper subterm of A's left-hand side, the empty result is "
                 f"returned as the single token NONE.\n"
                 f"Give the answer as the two resulting terms in prefix "
                 f"notation, A-side first, then the overlap-rewritten side, "
                 f"separated by ' ; '.")
        return block

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry.answer.strip() else 0.0
