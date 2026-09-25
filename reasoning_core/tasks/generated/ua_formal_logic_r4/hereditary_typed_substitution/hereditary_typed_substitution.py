import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'hereditary_typed_substitution (variant 3 of 3, unguided baseline)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_formal_logic_r4/hereditary_typed_substitution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1034322864,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _subst(term, var, repl):
    if _is_abs(term):
        _, bv, body = term
        newbody = body if bv == var else _subst(body, var, repl)
        return ("lam", bv, newbody)
    if isinstance(term, tuple):
        return tuple(_subst(t, var, repl) for t in term)
    if isinstance(term, str) and term == var:
        return repl
    return term


def _is_value(term):
    return isinstance(term, (int, str))


def _is_abs(term):
    return isinstance(term, tuple) and len(term) == 3 and term[0] == "lam"


def _is_app(term):
    return isinstance(term, tuple) and len(term) == 3 and term[0] == "app"


def _is_pair(term):
    return isinstance(term, tuple) and len(term) == 3 and term[0] == "pair"


def _is_proj(term):
    return isinstance(term, tuple) and len(term) == 3 and term[0] == "proj"


def _beta_reduce(term):
    while True:
        if isinstance(term, str) or isinstance(term, int):
            return term
        if _is_abs(term):
            _, bv, body = term
            nb = _beta_reduce(body)
            if nb == body:
                return ("lam", bv, body)
            term = ("lam", bv, nb)
            continue
        if _is_app(term):
            _, f, a = term
            if _is_abs(f):
                _, bv, body = f
                bsub = _subst(body, bv, a)
                term = _beta_reduce(bsub)
                continue
            nf = _beta_reduce(f)
            na = _beta_reduce(a)
            if _is_abs(nf):
                _, bv, body = nf
                bsub = _subst(body, bv, na)
                term = _beta_reduce(bsub)
                continue
            return ("app", nf, na)
        if _is_pair(term):
            return ("pair", _beta_reduce(term[1]), _beta_reduce(term[2]))
        if _is_proj(term):
            _, name, p = term
            pn = _beta_reduce(p)
            if _is_pair(pn):
                if name == "fst":
                    term = _beta_reduce(pn[1])
                    continue
                else:
                    term = _beta_reduce(pn[2])
                    continue
            return ("proj", name, pn)
        return term


def _render(t):
    if isinstance(t, str):
        return t
    if isinstance(t, int):
        return str(t)
    if _is_abs(t):
        _, bv, body = t
        return f"(\\{bv}.{_render(body)})"
    if _is_app(t):
        _, f, a = t
        return f"({_render(f)} {_render(a)})"
    if _is_pair(t):
        return f"(<{_render(t[1])},{_render(t[2])}>)"
    if _is_proj(t):
        return f"(proj{t[1]}({_render(t[2])}))"
    raise ValueError(t)


def _split_pair(s):
    depth = 0
    for i, ch in enumerate(s):
        if ch in "(<":
            depth += 1
        elif ch in ")>":
            depth -= 1
        elif ch == "," and depth == 0:
            return s[:i], s[i + 1:]
    raise ValueError(s)


def _parse_term(s, i):
    while i < len(s) and s[i] == " ":
        i += 1
    if i >= len(s):
        return None, i
    ch = s[i]
    if ch.isdigit() or (ch == "-" and i + 1 < len(s) and s[i + 1].isdigit()):
        j = i
        if ch == "-":
            j += 1
        while j < len(s) and s[j].isdigit():
            j += 1
        return int(s[i:j]), j
    if ch.islower():
        j = i
        while j < len(s) and s[j].islower():
            j += 1
        return s[i:j], j
    if ch == "(":
        if i + 1 < len(s) and s[i + 1] == "\\":
            j = i + 2
            while j < len(s) and s[j] != ".":
                j += 1
            bv = s[i + 2:j]
            body, k = _parse_term(s, j + 1)
            assert s[k] == ")" and body is not None
            return ("lam", bv, body), k + 1
        if i + 1 < len(s) and s[i + 1] == "<":
            inner = s[i + 2:]
            depth = 0
            comma = -1
            for m, c in enumerate(inner):
                if c in "(<":
                    depth += 1
                elif c in ")>":
                    depth -= 1
                if c == "," and depth == 0:
                    comma = m
                    break
            if comma < 0:
                raise ValueError(s)
            a, _ = _parse_term(inner[:comma], 0)
            b, pb = _parse_term(inner[comma + 1:], 0)
            k = i + 2 + comma + 1 + pb
            assert s[k] == ">"
            assert s[k + 1] == ")"
            return ("pair", a, b), k + 2
        if s.startswith("(proj", i):
            name = s[i + 5:i + 8]
            assert s[i + 8] == "("
            arg, k = _parse_term(s, i + 9)
            assert s[k] == ")"
            return ("proj", name, arg), k + 1
        arg, k = _parse_term(s, i + 1)
        assert s[k] == " "
        arg2, k2 = _parse_term(s, k + 1)
        assert s[k2] == ")"
        return ("app", arg, arg2), k2 + 1
    raise ValueError(s)


def _parse(s):
    term, end = _parse_term(s, 0)
    if term is None:
        raise ValueError(s)
    return term


VARS = ["x", "y", "z", "w", "u", "v"]


def _ran_var(exclude):
    pool = [v for v in VARS if v not in exclude]
    return random.choice(pool)


@dataclass
class HereditaryTypedConfig(Config):
    depth: int = 2
    nvars: int = 2
    redex_prob: float = 0.5

    def apply_difficulty(self, level):
        self.depth = stochastic_rounding(self.depth + level)
        self.nvars = min(6, stochastic_rounding(self.nvars + level // 2))
        self.redex_prob = 0.4 + 0.1 * min(level, 6)


def _gen_normal(maxdepth, bound):
    if maxdepth <= 0:
        return random.choice(["0", "1", "2"])
    kind = random.random()
    if kind < 0.3:
        return random.choice(["0", "1", "2"])
    if kind < 0.45:
        v = random.choice(VARS[:bound])
        return v
    if kind < 0.7:
        bv = random.choice(VARS[:max(bound, 1)])
        body = _gen_normal(maxdepth - 1, min(bound + 1, 6))
        return ("lam", bv, body)
    if kind < 0.85:
        a = _gen_normal(maxdepth - 1, bound)
        b = _gen_normal(maxdepth - 1, bound)
        return ("pair", a, b)
    if kind < 0.92:
        a = _gen_normal(maxdepth - 1, bound)
        b = _gen_normal(maxdepth - 1, bound)
        return ("proj", random.choice(["fst", "snd"]), ("pair", a, b))
    return ("app", _gen_normal(maxdepth - 1, bound), _gen_normal(maxdepth - 1, bound))


class HereditaryTypedSubstitution(Task):
    summary = ("Substitute normal terms into typed normal forms, immediately reducing redexes "
               "created by replacement; range over nested functions, products, and projections, "
               "returning the resulting beta-normal term.")
    config_cls = HereditaryTypedConfig

    def generate_entry(self):
        while True:
            var_index = random.randrange(min(self.config.nvars, len(VARS)))
            target_var = VARS[var_index]
            repl = _gen_normal(self.config.depth, self.config.nvars)
            body = _gen_normal(self.config.depth, self.config.nvars)
            if random.random() < self.config.redex_prob:
                bv = _ran_var({target_var})
                inner = _gen_normal(self.config.depth, self.config.nvars)
                body = ("app", ("lam", bv, inner), target_var)
            substituted = _subst(body, target_var, repl)
            result = _beta_reduce(substituted)
            reentered = _beta_reduce(substituted)
            if _render(result) != _render(reentered):
                continue
            if _is_value(result):
                continue
            answer = _render(result)
            prompt = self.render_prompt({
                "target": target_var,
                "repl": _render(repl),
                "term": _render(body),
            })
            if len(prompt.split()) > 380:
                continue
            return Entry(metadata={
                "target": target_var,
                "repl": _render(repl),
                "term": _render(body),
                "depth": self.config.depth,
            }, answer=answer)

    def render_prompt(self, metadata):
        return (
            "In the simply-typed lambda calculus with products, projects, and base numerals, "
            f"perform the substitution [{metadata['target']} := {metadata['repl']}] in the "
            f"normal-form term {metadata['term']}, then immediately reduce every redex created "
            "by the replacement until you reach a beta-normal form that is itself normal."
            " Write only the final beta-normal term, in the same surface syntax used above."
        )

    def score_answer(self, answer, entry):
        try:
            parsed = _parse(answer.strip())
        except Exception:
            return 0.0
        gold = _beta_reduce(_parse(entry.answer))
        return 1.0 if _render(parsed) == _render(gold) else 0.0
