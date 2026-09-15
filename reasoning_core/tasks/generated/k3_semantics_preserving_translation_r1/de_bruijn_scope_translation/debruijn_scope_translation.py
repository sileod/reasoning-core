import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'debruijn_scope_translation (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_semantics_preserving_translation_r1/debruijn_scope_translation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

_ALPHABET = list("abcdefghijk")


@dataclass
class DeBruijnScopeConfig(Config):
    max_depth: int = 3
    max_free: int = 2
    shadow_prob: float = 0.2

    def apply_difficulty(self, level):
        self.max_depth = 3 + level
        self.max_free = 2 + level
        self.shadow_prob = min(0.9, 0.2 + 0.1 * level)


def _gen_term(depth, enclosing, free_pool, shadow_prob):
    """Return a named lambda term: a str variable, ('lam', var, body) or ('app', f, g)."""
    if depth <= 0 or (depth == 1 and random.random() < 0.5):
        if enclosing and random.random() < 0.6:
            return random.choice(enclosing)
        return random.choice(free_pool) if free_pool else random.choice(_ALPHABET)
    if random.random() < 0.55:
        if enclosing and random.random() < shadow_prob:
            v = random.choice(enclosing)
        else:
            v = random.choice(_ALPHABET)
        body = _gen_term(depth - 1, [v] + enclosing, free_pool, shadow_prob)
        return ("lam", v, body)
    f = _gen_term(depth - 1, enclosing, free_pool, shadow_prob)
    g = _gen_term(depth - 1, enclosing, free_pool, shadow_prob)
    return ("app", f, g)


def _tree_has_lam(t):
    return not isinstance(t, str) and (t[0] == "lam" or _tree_has_lam(t[1]) or _tree_has_lam(t[2]))


def _has_bound(db):
    """True if the de Bruijn string contains at least one bound index (digits not after '#')."""
    n = len(db)
    i = 0
    while i < n:
        if db[i] == "#":
            i += 1
            while i < n and db[i].isdigit():
                i += 1
            continue
        if db[i].isdigit():
            return True
        i += 1
    return False


def _named_to_db(tree):
    frees = set()

    def collect(t, env):
        if isinstance(t, str):
            if t not in env:
                frees.add(t)
        elif t[0] == "lam":
            collect(t[2], [t[1]] + env)
        else:
            collect(t[1], env)
            collect(t[2], env)

    collect(tree, [])
    free_map = {name: i for i, name in enumerate(sorted(frees))}
    out = []

    def go(t, env):
        if isinstance(t, str):
            if t in env:
                out.append(str(env.index(t)))
            else:
                out.append("#%d" % free_map[t])
        elif t[0] == "lam":
            out.append("\\")
            go(t[2], [t[1]] + env)
        else:
            out.append("(")
            go(t[1], env)
            out.append(" ")
            go(t[2], env)
            out.append(")")

    go(tree, [])
    return "".join(out)


def _tokenize(s, i):
    if s[i] == "#":
        j = i + 1
        while j < len(s) and s[j].isdigit():
            j += 1
        return ("free", int(s[i + 1:j])), j
    j = i
    while j < len(s) and s[j].isdigit():
        j += 1
    return ("bound", int(s[i:j])), j


def _parse_db(s):
    def p(pos):
        c = s[pos]
        if c == "\\":
            t, pos2 = p(pos + 1)
            return ("lam", t), pos2
        if c == "(":
            f, pos2 = p(pos + 1)
            assert s[pos2] == " "
            g, pos3 = p(pos2 + 1)
            assert s[pos3] == ")"
            return ("app", f, g), pos3 + 1
        tok, pos2 = _tokenize(s, pos)
        return tok, pos2

    t, end = p(0)
    assert end == len(s)
    return t


def _db_to_named(tree):
    ctr = [0]

    def go(t, env):
        if t[0] == "lam":
            v = "x%d" % ctr[0]
            ctr[0] += 1
            return ("lam", v, go(t[1], [v] + env))
        if t[0] == "app":
            return ("app", go(t[1], env), go(t[2], env))
        if t[0] == "bound":
            return env[t[1]]
        return "f%d" % t[1]

    return go(tree, [])


def _named_str(t):
    if isinstance(t, str):
        return t
    if t[0] == "lam":
        return "\\%s. %s" % (t[1], _named_str(t[2]))
    return "(%s %s)" % (_named_str(t[1]), _named_str(t[2]))


class DeBruijnScopeTranslationV1(Task):
    task_name = "de_bruijn_scope_translation"
    summary = ("Translate lambda terms from named-variable syntax into de Bruijn index form "
               "across nested binders, shadowing and free variables, numbering bound variables "
               "by binder distance and free variables by sorted placeholder indices; the answer "
               "is the converted term with binder structure intact, verified by the inverse "
               "round trip under fresh consistent naming.")
    design_choice = ("Answer as a canonical string with de Bruijn indices for bound variables "
                     "and numbered free-variable placeholders, preserving binder order.")
    config_cls = DeBruijnScopeConfig

    def generate_entry(self):
        cfg = self.config
        free_pool = random.sample(_ALPHABET, min(cfg.max_free, len(_ALPHABET)))
        for _ in range(300):
            tree = _gen_term(cfg.max_depth, [], free_pool, cfg.shadow_prob)
            if not _tree_has_lam(tree):
                continue
            db = _named_to_db(tree)
            if not db or db != db.strip() or not _has_bound(db):
                continue
            try:
                named2 = _db_to_named(_parse_db(db))
            except Exception:
                continue
            if _named_to_db(named2) != db:
                continue
            named = _named_str(tree)
            return Entry(metadata={
                "named": named,
                "max_depth": int(cfg.max_depth),
                "max_free": int(cfg.max_free),
                "shadow_prob": float(cfg.shadow_prob),
            }, answer=db)
        raise RuntimeError("failed to produce a valid de Bruijn translation after 300 attempts")

    def render_prompt(self, metadata):
        return (
            "Translate the lambda term below from named-variable syntax into de Bruijn index form. "
            "Rules: a bound variable becomes the number of binders standing between it and the "
            "binder that captures it (the innermost binder gives 0, the next 1, and so on); a free "
            "variable becomes #k where k is its rank when all distinct free variables are sorted "
            "alphabetically (so the alphabetically first free variable is #0); an abstraction "
            "\\x.M becomes \\ followed by the conversion of M; an application (M N) stays "
            "(M N) with a single space. Give only the converted term.\n\n"
            f"Lambda term: {metadata['named']}\n\n"
            "Example: \\a. a b converts to \\(0 #0).\n"
            "Answer:"
        )


