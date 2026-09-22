import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Entry, Task


NAME_POOL = ["a", "b", "c", "d", "e", "f", "g", "p", "q", "r", "s", "t", "u"]


# --- term helpers (terms are tuples) ---------------------------------------
# var   -> ('var', name)
# lam   -> ('lam', binder, body)
# app   -> ('app', fun, arg)
# call  -> ('call', macro_name, (arg0, arg1, ...))


def term_free(term):
    if term[0] == "var":
        return {term[1]}
    if term[0] == "lam":
        return term_free(term[2]) - {term[1]}
    if term[0] == "app":
        return term_free(term[1]) | term_free(term[2])
    out = set()
    for a in term[2]:
        out |= term_free(a)
    return out


def term_names(term):
    if term[0] == "var":
        return {term[1]}
    if term[0] == "lam":
        return {term[1]} | term_names(term[2])
    if term[0] == "app":
        return term_names(term[1]) | term_names(term[2])
    out = set()
    for a in term[2]:
        out |= term_names(a)
    return out


def rename_term(term, old, new):
    """Rename the binder old (and its bound occurrences) to new inside term."""
    if term[0] == "var":
        return ("var", new) if term[1] == old else term
    if term[0] == "lam":
        b = term[1]
        body = rename_term(term[2], old, new)
        return ("lam", (new if b == old else b), body)
    if term[0] == "app":
        return ("app", rename_term(term[1], old, new), rename_term(term[2], old, new))
    return ("call", term[1], tuple(rename_term(a, old, new) for a in term[2]))


def subst_term(term, var, rep, counter, busy, exempt):
    """Capture-avoiding substitution of var -> rep inside term.

    Binders colliding with a free variable of ``rep`` are fresh-renamed unless
    their name is declared capture-exempt (``exempt``); that exemption is the
    task's "declared capture exemption".
    """
    if term[0] == "var":
        return rep if term[1] == var else term
    if term[0] == "lam":
        bname = term[1]
        if bname == var:
            return term
        frep = term_free(rep)
        if bname in frep and bname not in exempt:
            new = counter.fresh(busy)
            body = rename_term(term[2], bname, new)
            inner = subst_term(body, var, rep, counter, busy, exempt)
            return ("lam", new, inner)
        inner = subst_term(term[2], var, rep, counter, busy, exempt)
        return ("lam", bname, inner)
    if term[0] == "app":
        return ("app", subst_term(term[1], var, rep, counter, busy, exempt),
                subst_term(term[2], var, rep, counter, busy, exempt))
    return ("call", term[1], tuple(subst_term(a, var, rep, counter, busy, exempt) for a in term[2]))


class Fresh:
    """Deterministic fresh-name counter: base_0, base_1, ... not colliding with busy."""

    def __init__(self, busy, base):
        self._busy = busy
        self._base = base

    def fresh(self, busy):
        idx = 0
        while True:
            cand = "%s_%d" % (self._base, idx)
            idx += 1
            if cand not in busy:
                busy.add(cand)
                return cand


def expand(term, macros, counter, busy, depth):
    """Fully expand every macro call, recursively, applying hygiene renamings."""
    if term[0] == "var" or term[0] == "lam":
        body = expand(term[2], macros, counter, busy, depth) if term[0] == "lam" else None
        if term[0] == "lam":
            return ("lam", term[1], body)
        return term
    if term[0] == "app":
        return ("app", expand(term[1], macros, counter, busy, depth),
                expand(term[2], macros, counter, busy, depth))
    mname = term[1]
    args = term[2]
    params, body, exempt = macros[mname]
    eargs = [expand(a, macros, counter, busy, depth) for a in args]
    acc = body
    for p, a in zip(params, eargs):
        acc = subst_term(acc, p, a, counter, busy, exempt)
    return expand(acc, macros, counter, busy, depth)


def render(term):
    if term[0] == "var":
        return term[1]
    if term[0] == "lam":
        return "\\%s. %s" % (term[1], render(term[2]))
    if term[0] == "call":
        return "(%s %s)" % (term[1], " ".join(render(a) for a in term[2]))
    return "(%s %s)" % (render(term[1]), render(term[2]))


# --- instance construction ---------------------------------------------------

def build_body(macros, defined, mac_names, params, depth, rng, pdepth):
    """Build a random lambda term over the given params, possibly calling macros.

    ``macros`` maps name -> (params, body, exempt). When this returns, the term is
    stored so later macros may reference it (DAG, guaranteeing termination)."""
    kind = rng.random()
    if kind < 0.30 and defined and depth > 0:
        m = rng.choice(defined)
        margs = tuple(build_arg_term(params, rng, pdepth) for _ in range(len(macros[m][0])))
        return ("call", m, margs)
    if depth > 0 and rng.random() < 0.25:
        v = rng.choice(params)
        return ("lam", v, build_body(macros, defined, mac_names, params, depth - 1, rng, pdepth))
    if rng.random() < 0.35:
        f = build_arg_term(params, rng, pdepth)
        a = build_arg_term(params, rng, pdepth)
        return ("app", f, a)
    return ("var", rng.choice(params))


def build_arg_term(params, rng, pdepth):
    """An argument term (a full term that may bind its own variables)."""
    if rng.random() < 0.35 and pdepth > 0:
        v = rng.choice(NAME_POOL)
        return ("lam", v, build_arg_term(params, rng, pdepth - 1))
    if rng.random() < 0.35:
        return ("app", build_arg_term(params, rng, pdepth - 1),
                build_arg_term(params, rng, pdepth - 1))
    return ("var", rng.choice(params))


def generate_macros(rng, n_macros, max_depth, max_pdepth, max_params, exempt_prob):
    macros = {}
    defined = []
    mac_names = []
    mac_bodies = {}
    for i in range(n_macros):
        name = "M%d" % i
        mac_names.append(name)
        nparams = rng.randint(1, max_params)
        params = rng.sample(NAME_POOL, nparams)
        depth = rng.randint(0, max_depth)
        body = build_body(macros, defined, mac_names, params, depth, rng, max_pdepth)
        exempt = frozenset(n for n in params if rng.random() < exempt_prob)
        macros[name] = (params, body, exempt)
        mac_bodies[name] = body
        defined.append(name)
    return macros


@dataclass
class MacroConfig(Config):
    n_macros: int = 1
    max_depth: int = 1
    max_pdepth: int = 1
    max_params: int = 2
    exempt_prob: float = 0.3
    top_params: int = 2

    def apply_difficulty(self, level):
        self.n_macros = 1 + level
        self.max_depth = 1 + int(level * 0.7)
        self.max_pdepth = 1 + int(level * 0.6)
        self.max_params = 2 + (level >= 3)
        self.exempt_prob = 0.2 + 0.1 * random.random()
        self.top_params = 2 + (level >= 2)


class MacroHygieneExpansion(Task):
    summary = ("Expand recursive macro calls through capture-avoiding substitution with declared "
               "capture-exempt binder names, renaming captured binders via a deterministic fresh "
               "counter; answer the fully renamed expanded term.")
    design_choice = ("Instances present a macro call in a small lambda calculus with explicit binder "
                     "syntax; the answer is the fully expanded term after all recursive expansions, "
                     "with fresh names chosen from a deterministic counter.")
    config_cls = MacroConfig
    task_version = 2

    def _expanded(self):
        rng = random
        n = self.config.n_macros
        macros = generate_macros(rng, n, self.config.max_depth, self.config.max_pdepth,
                                 self.config.max_params, self.config.exempt_prob)
        mname = "M%d" % rng.randrange(n)
        params = macros[mname][0]
        neargs = min(len(params), 1 + rng.randrange(min(max(len(params), 1), self.config.top_params)))
        args = tuple(build_arg_term(params, rng, self.config.max_pdepth) for _ in range(neargs))
        call = ("call", mname, args)
        busy = set()
        for term in _collect(macros):
            busy |= term_names(term)
        for a in args:
            busy |= term_names(a)
        counter = Fresh(busy, "x")
        result = expand(call, macros, counter, busy, 0)
        return macros, call, result

    def generate_entry(self):
        while True:
            macros, call, result = self._expanded()
            answer = render(result)
            allnames = [nm for ((_p, _b, _e), nm) in
                        [(macros[m], m) for m in macros]]  # unused; kept simple
            if "M" in answer:
                continue
            break
        payload = {
            "macros": _render_macros(macros),
            "call": render(call),
        }
        return Entry(metadata={"payload": payload, "macros": _render_macros(macros),
                               "call": render(call), "answer_syntax": "lambda term",
                               "fresh_base": "x"}, answer=answer)

    def render_prompt(self, metadata):
        lines = [
            "Consider the following macros, where a call `(M a1 ... ak)` is expanded by replacing",
            "each parameter of M's body with the matching argument. Arguments are expanded to values",
            "first. During substitution, if a binder inside a macro body would capture a free variable",
            "of an argument, that binder is renamed to a fresh name `x_0`, `x_1`, ... so no unintended",
            "capture occurs. A macro marked `[exempt: ...]` lists binder names that are NOT renamed",
            "(capture by those binders is the declared intent).",
            "",
        ]
        lines.append("Macros:")
        lines.append(metadata["macros"])
        lines.append("")
        lines.append("Expand this call completely:")
        lines.append(metadata["call"])
        lines.append("")
        lines.append("What is the fully expanded term, with all macro calls resolved and binders")
        lines.append("renamed exactly as described? Give the term using lambda syntax consisting of")
        lines.append("a binder `\\name <term>`, application `(f a)`, and variable names.")
        return "\n".join(lines)


def _collect(macros):
    out = []
    for m in macros:
        out.append(macros[m][1])
    return out


def _render_macros(macros):
    parts = []
    for m in macros:
        params, body, exempt = macros[m]
        ex = "".join(sorted(exempt))
        tag = ("  [exempt: %s]" % ", ".join(sorted(exempt))) if exempt else ""
        head = "%s(%s)" % (m, ", ".join(params))
        line = "%s = %s%s" % (head, render(body), tag)
        parts.append(line)
    return "\n".join(parts)


TASK_META = {'parent_source_id': None,
 'idea': 'macro_hygiene_expansion (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_language_implementation_r4/macro_hygiene_expansion',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
                                         'version': 'bubblewrap 0.8.0'}}}}
