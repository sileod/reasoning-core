"""Symbolic rewriting: λ-calculus β-reduction.

- `lambda_reduction` — reduce an untyped λ-term to β-normal form.
  Instances are built by *anti-reduction*: sample an NF, then insert redexes
  that reduce back to it. Three elementary moves:
      1. dummy        (λx.M) N          x ∉ FV(M)
      2. identity     (λx.x) M
      3. substitution (λx.M[T↦x]) T     (optionally duplicating T)
  Move 3 can fail capture-avoidance silently; we catch it by normalising the
  result and checking α-equivalence with the target NF.
"""
from dataclasses import dataclass
import ast, random, re

from reasoning_core.template import Task, Problem, Config, Payload, edict


# ─────────────────────────────────────────────────────────────────────────────
# λ-calculus core
# ─────────────────────────────────────────────────────────────────────────────
# term ::= ('v', name) | ('l', name, body) | ('a', fun, arg)

def _fv(t):
    k = t[0]
    if k == 'v': return {t[1]}
    if k == 'l': return _fv(t[2]) - {t[1]}
    return _fv(t[1]) | _fv(t[2])

def _all_names(t):
    k = t[0]
    if k == 'v': return {t[1]}
    if k == 'l': return _all_names(t[2]) | {t[1]}
    return _all_names(t[1]) | _all_names(t[2])

def _fresh(avoid):
    i = 0
    while (n := f"_{i}") in avoid: i += 1
    return n

def _subst(t, x, s):
    k = t[0]
    if k == 'v': return s if t[1] == x else t
    if k == 'a': return ('a', _subst(t[1], x, s), _subst(t[2], x, s))
    y, body = t[1], t[2]
    if y == x: return t
    if y in _fv(s):
        y2 = _fresh(_fv(body) | _fv(s) | {x})
        body, y = _subst(body, y, ('v', y2)), y2
    return ('l', y, _subst(body, x, s))

def _step(t):
    """One leftmost-outermost β-step; None if already in NF."""
    k = t[0]
    if k == 'a':
        f, a = t[1], t[2]
        if f[0] == 'l': return _subst(f[2], f[1], a)
        if (f2 := _step(f)) is not None: return ('a', f2, a)
        if (a2 := _step(a)) is not None: return ('a', f, a2)
    elif k == 'l':
        if (b2 := _step(t[2])) is not None: return ('l', t[1], b2)
    return None

def _normalize(t, max_steps=200):
    for _ in range(max_steps):
        n = _step(t)
        if n is None: return t
        t = n
    return None

def _pretty(t):
    if t[0] == 'v': return t[1]
    if t[0] == 'l': return f"(\\{t[1]}.{_pretty(t[2])})"
    return f"({_pretty(t[1])} {_pretty(t[2])})"

def _debruijn(t, env=()):
    k = t[0]
    if k == 'v':
        return f"#{env.index(t[1])}" if t[1] in env else t[1]
    if k == 'l': return f"(\\.{_debruijn(t[2], (t[1],) + env)})"
    return f"({_debruijn(t[1], env)} {_debruijn(t[2], env)})"

_LAM_TOK = re.compile(r'[()\\.\u03bb]|[A-Za-z_]\w*')

def _parse_lam(s: str):
    toks, i = _LAM_TOK.findall(s), [0]
    def peek(): return toks[i[0]] if i[0] < len(toks) else None
    def pop():  t = peek(); i[0] += 1; return t
    def atom():
        t = peek()
        if t == '(':
            pop(); e = expr()
            if pop() != ')': raise ValueError("missing )")
            return e
        if t in ('\\', 'λ'):
            pop(); name = pop()
            if pop() != '.': raise ValueError("missing .")
            return ('l', name, expr())
        if t is None or t in (')', '.'):
            raise ValueError(f"unexpected {t!r}")
        return ('v', pop())
    def expr():
        e = atom()
        while peek() not in (None, ')'):
            e = ('a', e, atom())
        return e
    out = expr()
    if i[0] != len(toks): raise ValueError("trailing tokens")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Anti-reduction: sample NF, then insert redexes that reduce back to it
# ─────────────────────────────────────────────────────────────────────────────
_LAM_CONSTS = ['a', 'b', 'c', 'd']

def _gen_nf(depth, rng, env):
    """Sample a β-normal term.
        NF       ::=  λx.NF  |  neutral
        neutral  ::=  (var|const) NF*          (head is never a λ)
    """
    if depth > 0 and rng.random() < 0.35:
        name = f"v{len(env)}"
        return ('l', name, _gen_nf(depth - 1, rng, env + (name,)))
    head = ('v', rng.choice(env) if env and rng.random() < 0.7
                  else rng.choice(_LAM_CONSTS))
    n_args = 0 if depth <= 0 else rng.randint(0, 2)
    t = head
    for _ in range(n_args):
        t = ('a', t, _gen_nf(depth - 1, rng, env))
    return t

def _positions(t, path=()):
    yield path, t
    if t[0] == 'a':
        yield from _positions(t[1], path + (1,))
        yield from _positions(t[2], path + (2,))
    elif t[0] == 'l':
        yield from _positions(t[2], path + (2,))

def _replace_at(t, path, new):
    if not path: return new
    i, rest = path[0], path[1:]
    if t[0] == 'a':
        return (('a', _replace_at(t[1], rest, new), t[2]) if i == 1
                else ('a', t[1], _replace_at(t[2], rest, new)))
    return ('l', t[1], _replace_at(t[2], rest, new))

def _replace_all(t, target, new):
    if t == target: return new
    if t[0] == 'a':
        return ('a', _replace_all(t[1], target, new),
                     _replace_all(t[2], target, new))
    if t[0] == 'l':
        return ('l', t[1], _replace_all(t[2], target, new))
    return t

def _insert_redex(M, rng, arg_depth):
    """One anti-reduction move at a random subterm of M."""
    path, S = rng.choice(list(_positions(M)))
    x = _fresh(_all_names(M))
    inner = [(p, s) for p, s in _positions(S) if p]
    r = rng.random()

    if r < 0.2 or not inner:                        # dummy:    (λx.S) N
        N = _gen_nf(rng.randint(0, min(2, arg_depth)), rng, ())
        new = ('a', ('l', x, S), N)
    elif r < 0.35:                                  # identity: (λx.x) S
        new = ('a', ('l', x, ('v', x)), S)
    else:                                           # subst:    (λx.S[T↦x]) T
        _, T = rng.choice(inner)
        hits = [p for p, s in inner if s == T]
        S_abs = (_replace_all(S, T, ('v', x)) if rng.random() < 0.5
                 else _replace_at(S, rng.choice(hits), ('v', x)))
        new = ('a', ('l', x, S_abs), T)

    return _replace_at(M, path, new)


@dataclass
class LambdaReductionConfig(Config):
    nf_depth: int = 2
    n_insertions: int = 1

    def update(self, c=1):
        self.nf_depth     += c
        self.n_insertions += c


class LambdaReduction(Task):
    def __init__(self, config=None):
        super().__init__(config=config or LambdaReductionConfig())

    def generate(self):
        rng = random.Random()
        cfg = self.config
        for _ in range(500):
            nf = _gen_nf(cfg.nf_depth, rng, ())
            if not (3 <= len(_pretty(nf)) <= 60): continue
            if _step(nf) is not None: continue        # invariant guard

            t = nf
            for _ in range(cfg.n_insertions):
                t2 = _insert_redex(t, rng, cfg.nf_depth)
                if len(_pretty(t2)) > 200: break       # stop growing
                t = t2

            if _step(t) is None: continue              # no redex committed
            result = _normalize(t)
            if result is None: continue                # diverged
            if _debruijn(result) != _debruijn(nf):     # move 3 captured
                continue

            return Problem(
                metadata=edict(term=_pretty(t), normal_form=_pretty(nf)),
                answer=_pretty(nf),
            )
        raise RuntimeError("could not sample a valid λ-term")

    def prompt(self, metadata):
        return (
            "Reduce the following untyped λ-term to β-normal form.\n"
            "Syntax: `\\x.body` is λx.body; juxtaposition is left-associative application; free identifiers are constants.\n\n"
            f"Term: {metadata['term']}\n\n"
            "The answer is the β-normal form (compared up to α-equivalence)."
        )

    def score_answer(self, answer, entry):
        if answer is None: return 0.0
        try:
            got = _parse_lam(str(answer).strip())
        except Exception:
            return 0.0
        ref = _parse_lam(entry.answer)
        return float(_debruijn(got) == _debruijn(ref))








@dataclass(frozen=True)
class Rule:
    name: str
    lhs: object
    rhs: object


def _rw_isvar(t):
    return isinstance(t, str) and t[:1].isupper()


def _rw_show(t):
    if isinstance(t, tuple):
        return f"{t[0]}({','.join(_rw_show(x) for x in t[1:])})"
    return str(t)


def _rw_vars(t):
    if _rw_isvar(t):
        return {t}
    if isinstance(t, tuple):
        return set().union(*(_rw_vars(x) for x in t[1:])) if len(t) > 1 else set()
    return set()


def _rw_match(p, t, env=None):
    env = {} if env is None else dict(env)

    if _rw_isvar(p):
        if p in env:
            return env if env[p] == t else None
        env[p] = t
        return env

    if isinstance(p, tuple):
        if not isinstance(t, tuple) or p[0] != t[0] or len(p) != len(t):
            return None
        for a, b in zip(p[1:], t[1:]):
            env = _rw_match(a, b, env)
            if env is None:
                return None
        return env

    return env if p == t else None


def _rw_subst(t, env):
    if _rw_isvar(t):
        return env[t]
    if isinstance(t, tuple):
        return (t[0], *[_rw_subst(x, env) for x in t[1:]])
    return t


def _rw_positions(t, path=()):
    yield path, t
    if isinstance(t, tuple):
        for i, x in enumerate(t[1:], 1):
            yield from _rw_positions(x, path + (i,))


def _rw_replace(t, path, new):
    if not path:
        return new
    i, rest = path[0], path[1:]
    args = list(t[1:])
    args[i - 1] = _rw_replace(args[i - 1], rest, new)
    return (t[0], *args)


def _rw_step(t, rules):
    for r in rules:
        env = _rw_match(r.lhs, t)
        if env is not None:
            return _rw_subst(r.rhs, env), r.name

    if isinstance(t, tuple):
        for i, x in enumerate(t[1:], 1):
            out = _rw_step(x, rules)
            if out is not None:
                x2, name = out
                args = list(t[1:])
                args[i - 1] = x2
                return (t[0], *args), name

    return None


def _rw_trace(t, rules, max_steps=200):
    terms, names = [t], []
    for _ in range(max_steps):
        out = _rw_step(t, rules)
        if out is None:
            return terms, names
        t, name = out
        terms.append(t)
        names.append(name)
    return None, names


def _rw_normalize(t, rules, max_steps=200):
    terms, names = _rw_trace(t, rules, max_steps)
    if terms is None:
        return None, names
    return terms[-1], names


_RW_TOK = re.compile(r'[A-Za-z_]\w*|[(),]')


def _rw_parse(s):
    toks, i = _RW_TOK.findall(s), [0]

    def peek():
        return toks[i[0]] if i[0] < len(toks) else None

    def pop():
        t = peek()
        i[0] += 1
        return t

    def term():
        name = pop()
        if name is None or name in '(),':
            raise ValueError("bad term")
        if peek() != '(':
            return name

        pop()
        args = []
        if peek() != ')':
            while True:
                args.append(term())
                if peek() != ',':
                    break
                pop()

        if pop() != ')':
            raise ValueError("missing )")

        return (name, *args)

    out = term()
    if i[0] != len(toks):
        raise ValueError("trailing tokens")
    return out


def _rw_gen_ground(depth, rng, consts, heads):
    if depth <= 0 or rng.random() < 0.42:
        return rng.choice(consts)
    f, arity = rng.choice(heads)
    return (f, *[_rw_gen_ground(depth - 1, rng, consts, heads) for _ in range(arity)])


def _rw_fill_env(vars_, env, rng, consts, heads, depth, rules):
    env = dict(env)
    for v in sorted(vars_):
        if v in env:
            continue
        t = _rw_gen_ground(rng.randint(0, depth), rng, consts, heads)
        t, _ = _rw_normalize(t, rules)
        if t is None:
            return None
        env[v] = t
    return env


def _rw_insert_redex(t, rules, rng, consts, heads, depth):
    positions = list(_rw_positions(t))
    rng.shuffle(positions)

    rs = list(rules)
    rng.shuffle(rs)

    for path, sub in positions:
        for r in rs:
            env = _rw_match(r.rhs, sub)
            if env is None:
                continue

            env = _rw_fill_env(_rw_vars(r.lhs), env, rng, consts, heads, depth, rules)
            if env is None:
                continue

            redex = _rw_subst(r.lhs, env)
            if redex != sub:
                return _rw_replace(t, path, redex), r.name

    return None, None


def _rw_rule_text(rules):
    return '\n'.join(f"- {_rw_show(r.lhs)} -> {_rw_show(r.rhs)}" for r in rules)


def _rw_pack_arith():
    X, Y, Z = 'X', 'Y', 'Z'
    return edict(
        name='arith',
        consts=['0', '1', '2', 'a', 'b', 'c'],
        heads=[('add', 2), ('mul', 2), ('sub', 2), ('neg', 1), ('pow', 2)],
        rules=[
            Rule('add_zero_l', ('add', '0', X), X),
            Rule('add_zero_r', ('add', X, '0'), X),
            Rule('mul_one_l',  ('mul', '1', X), X),
            Rule('mul_one_r',  ('mul', X, '1'), X),
            Rule('mul_zero_l', ('mul', '0', X), '0'),
            Rule('mul_zero_r', ('mul', X, '0'), '0'),
            Rule('sub_zero',   ('sub', X, '0'), X),
            Rule('sub_self',   ('sub', X, X), '0'),
            Rule('neg_neg',    ('neg', ('neg', X)), X),
            Rule('pow_one',    ('pow', X, '1'), X),
            Rule('pow_zero',   ('pow', X, '0'), '1'),
            Rule('factor_l',   ('add', ('mul', X, Y), ('mul', X, Z)), ('mul', X, ('add', Y, Z))),
        ],
    )


def _rw_pack_bool():
    X, Y = 'X', 'Y'
    return edict(
        name='bool',
        consts=['true', 'false', 'a', 'b', 'c'],
        heads=[('and', 2), ('or', 2), ('not', 1), ('if', 3), ('eq', 2)],
        rules=[
            Rule('and_true_l',  ('and', 'true', X), X),
            Rule('and_true_r',  ('and', X, 'true'), X),
            Rule('and_false_l', ('and', 'false', X), 'false'),
            Rule('and_false_r', ('and', X, 'false'), 'false'),
            Rule('and_idem',    ('and', X, X), X),
            Rule('or_false_l',  ('or', 'false', X), X),
            Rule('or_false_r',  ('or', X, 'false'), X),
            Rule('or_true_l',   ('or', 'true', X), 'true'),
            Rule('or_true_r',   ('or', X, 'true'), 'true'),
            Rule('or_idem',     ('or', X, X), X),
            Rule('not_not',     ('not', ('not', X)), X),
            Rule('if_true',     ('if', 'true', X, Y), X),
            Rule('if_false',    ('if', 'false', X, Y), Y),
            Rule('eq_self',     ('eq', X, X), 'true'),
        ],
    )


def _rw_pack_list():
    X, XS, YS = 'X', 'XS', 'YS'
    return edict(
        name='list',
        consts=['nil', 'a', 'b', 'c', '0'],
        heads=[('cons', 2), ('append', 2), ('head', 1), ('tail', 1), ('len', 1), ('s', 1)],
        rules=[
            Rule('append_nil',  ('append', 'nil', XS), XS),
            Rule('append_cons', ('append', ('cons', X, XS), YS), ('cons', X, ('append', XS, YS))),
            Rule('head_cons',   ('head', ('cons', X, XS)), X),
            Rule('tail_cons',   ('tail', ('cons', X, XS)), XS),
            Rule('len_nil',     ('len', 'nil'), '0'),
            Rule('len_cons',    ('len', ('cons', X, XS)), ('s', ('len', XS))),
        ],
    )


def _rw_pack_ast():
    X, Y = 'X', 'Y'
    return edict(
        name='ast',
        consts=['unit', 'true', 'false', 'a', 'b', 'c'],
        heads=[('pair', 2), ('fst', 1), ('snd', 1), ('id', 1), ('const', 2), ('if', 3), ('let', 2)],
        rules=[
            Rule('fst_pair', ('fst', ('pair', X, Y)), X),
            Rule('snd_pair', ('snd', ('pair', X, Y)), Y),
            Rule('id',       ('id', X), X),
            Rule('const',    ('const', X, Y), X),
            Rule('if_true',  ('if', 'true', X, Y), X),
            Rule('if_false', ('if', 'false', X, Y), Y),
            Rule('let_unit', ('let', 'unit', X), X),
        ],
    )


def _rw_pack_string():
    X, Y, Z = 'X', 'Y', 'Z'
    return edict(
        name='string',
        consts=['eps', 'a', 'b', 'c'],
        heads=[('cat', 2), ('rev', 1), ('quote', 1), ('lower', 1), ('upper', 1)],
        rules=[
            Rule('cat_eps_l',   ('cat', 'eps', X), X),
            Rule('cat_eps_r',   ('cat', X, 'eps'), X),
            Rule('cat_assoc',   ('cat', ('cat', X, Y), Z), ('cat', X, ('cat', Y, Z))),
            Rule('rev_eps',     ('rev', 'eps'), 'eps'),
            Rule('rev_rev',     ('rev', ('rev', X)), X),
            Rule('quote_quote', ('quote', ('quote', X)), ('quote', X)),
            Rule('lower_lower', ('lower', ('lower', X)), ('lower', X)),
            Rule('upper_upper', ('upper', ('upper', X)), ('upper', X)),
        ],
    )


def _rw_pack_logic():
    X, Y, Z = 'X', 'Y', 'Z'
    return edict(
        name='logic',
        consts=['true', 'false', 'p', 'q', 'r'],
        heads=[('imp', 2), ('iff', 2), ('xor', 2), ('not', 1), ('and', 2), ('or', 2)],
        rules=[
            Rule('imp_true_l',  ('imp', 'true', X), X),
            Rule('imp_false_l', ('imp', 'false', X), 'true'),
            Rule('imp_true_r',  ('imp', X, 'true'), 'true'),
            Rule('imp_false_r', ('imp', X, 'false'), ('not', X)),
            Rule('iff_self',    ('iff', X, X), 'true'),
            Rule('xor_self',    ('xor', X, X), 'false'),
            Rule('xor_false_l', ('xor', 'false', X), X),
            Rule('xor_false_r', ('xor', X, 'false'), X),
            Rule('xor_true_l',  ('xor', 'true', X), ('not', X)),
            Rule('xor_true_r',  ('xor', X, 'true'), ('not', X)),
            Rule('not_not',     ('not', ('not', X)), X),
            Rule('demorgan',    ('not', ('and', X, Y)), ('or', ('not', X), ('not', Y))),
        ],
    )


def _rw_pack_path():
    X, Y, Z = 'X', 'Y', 'Z'
    return edict(
        name='path',
        consts=['root', 'home', 'tmp', 'a', 'b', 'c', 'dot'],
        heads=[('join', 2), ('parent', 1), ('base', 1), ('norm', 1)],
        rules=[
            Rule('join_dot_l',   ('join', 'dot', X), X),
            Rule('join_dot_r',   ('join', X, 'dot'), X),
            Rule('join_root_l',  ('join', 'root', X), ('norm', X)),
            Rule('norm_norm',    ('norm', ('norm', X)), ('norm', X)),
            Rule('base_join',    ('base', ('join', X, Y)), Y),
            Rule('parent_join',  ('parent', ('join', X, Y)), X),
            Rule('join_assoc',   ('join', ('join', X, Y), Z), ('join', X, ('join', Y, Z))),
        ],
    )


_RW_PACKS = [
    _rw_pack_arith,
    _rw_pack_bool,
    _rw_pack_list,
    _rw_pack_ast,
    _rw_pack_string,
    _rw_pack_logic,
    _rw_pack_path,
]


@dataclass
class RewriteSystemConfig(Config):
    depth: int = 3
    n_insertions: int = 3
    min_rules: int = 5
    max_rules: int = 9
    min_steps: int = 2
    max_steps: int = 160
    max_chars: int = 520
    atom_keep_prob: float = 0.65
    shortcut_compression: float = 16.0

    def update(self, c=1):
        k = max(1, int(round(c)))
        self.depth += k
        self.n_insertions += k
        self.max_rules = min(self.max_rules + k, 12)
        self.min_steps += k
        self.max_steps += 50 * k
        self.max_chars += 120 * k
        self.atom_keep_prob = max(0.35, self.atom_keep_prob - 0.05 * k)
        self.shortcut_compression = max(8.0, self.shortcut_compression - 2.0 * k)


class RewriteSystem(Task):
    def __init__(self, config=None):
        super().__init__(config=config or RewriteSystemConfig())

    def _sample_rules(self, pack, rng):
        lo = min(self.config.min_rules, len(pack.rules))
        hi = min(self.config.max_rules, len(pack.rules))
        return rng.sample(pack.rules, rng.randint(lo, hi))

    @staticmethod
    def _format_trace(terms):
        lines = [f"-> {_rw_show(u)}" for u in terms[1:]]
        lines.append(f"normal_form: {_rw_show(terms[-1])}")
        return '\n'.join(lines)

    def generate(self):
        rng = random.Random()
        cfg = self.config

        for _ in range(2000):
            pack = rng.choice(_RW_PACKS)()
            rules = self._sample_rules(pack, rng)

            seed = _rw_gen_ground(cfg.depth, rng, pack.consts, pack.heads)
            nf, _ = _rw_normalize(seed, rules, cfg.max_steps)
            if nf is None:
                continue

            t = nf
            inserted = []
            for _ in range(cfg.n_insertions):
                t2, name = _rw_insert_redex(t, rules, rng, pack.consts, pack.heads, cfg.depth)
                if t2 is None:
                    continue
                if len(_rw_show(t2)) > cfg.max_chars:
                    continue
                t = t2
                inserted.append(name)

            if not inserted or t == nf:
                continue

            terms, used = _rw_trace(t, rules, cfg.max_steps)
            if terms is None or terms[-1] != nf:
                continue
            if len(used) < cfg.min_steps:
                continue

            term_s, nf_s = _rw_show(t), _rw_show(nf)
            if len(term_s) / max(1, len(nf_s)) > cfg.shortcut_compression and len(used) <= cfg.min_steps + 1:
                continue
            if not isinstance(nf, tuple) and rng.random() > cfg.atom_keep_prob:
                continue

            rules_s = _rw_rule_text(rules)
            cot = self._format_trace(terms)
            if len(rules_s) + len(term_s) + len(nf_s) + len(cot) > cfg.max_chars * 3:
                continue

            meta = edict(
                theory=pack.name,
                rules=rules_s,
                term=term_s,
                normal_form=nf_s,
                used=used,
                cot=cot,
            )
            meta.payload = Payload(rules=rules_s, term=term_s)
            return Problem(metadata=meta, answer=nf_s)

        raise RuntimeError("could not sample a rewrite-system instance")

    def prompt(self, metadata):
        return (
            "Normalize by the ordered rewrite rules. At each step, use the first "
            "applicable rule in the listed order, searching outermost-first and "
            "left-to-right.\n\n"
            f"{Payload(metadata['payload'])}\n\n"
            "The answer is the normal form."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0

        ans = str(answer).strip()
        ref = str(entry.answer).strip()

        if ans == ref:
            return 1.0

        if 'normal_form:' in ans:
            ans = ans.rsplit('normal_form:', 1)[-1].strip()

        try:
            got = _rw_parse(ans)
            target = _rw_parse(entry.metadata['normal_form'])
            return float(got == target)
        except Exception:
            return float(ans.replace(' ', '') == entry.metadata['normal_form'].replace(' ', ''))
