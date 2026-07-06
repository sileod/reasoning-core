"""Symbolic rewriting: λ-calculus β-reduction.

- `lambda_reduction` — reduce an untyped λ-term to β-normal form.
  Instances mix arbitrary λ-term sampling with *anti-reduction*: sample an NF,
  then insert redexes that reduce back to it. Three elementary moves:
      1. dummy        (λx.M) N          x ∉ FV(M)
      2. identity     (λx.x) M
      3. substitution (λx.M[T↦x]) T     (optionally duplicating T)
  Move 3 can fail capture-avoidance silently; we catch it by normalising the
  result and checking α-equivalence with the target NF.
"""
from dataclasses import dataclass
from collections import Counter
import ast, hashlib, random, re

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

def _term_size(t):
    if t[0] == 'v': return 1
    if t[0] == 'l': return 1 + _term_size(t[2])
    return 1 + _term_size(t[1]) + _term_size(t[2])

def _normalize_trace(t, max_steps=500):
    out = [t]
    for _ in range(max_steps):
        n = _step(t)
        if n is None: return out
        t = n
        out.append(t)
    return None

def _safe_normalize_trace(t, max_steps=500, max_size=2000):
    out = [t]
    try:
        for _ in range(max_steps):
            if _term_size(t) > max_size: return None
            n = _step(t)
            if n is None: return out
            t = n
            out.append(t)
    except RecursionError:
        return None
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

def _skeleton(t):
    if t[0] == 'v': return 'v'
    if t[0] == 'l': return ('l', _skeleton(t[2]))
    return ('a', _skeleton(t[1]), _skeleton(t[2]))

def _has_shadowing(t, bound=()):
    if t[0] == 'l':
        return t[1] in bound or _has_shadowing(t[2], bound + (t[1],))
    if t[0] == 'a':
        return _has_shadowing(t[1], bound) or _has_shadowing(t[2], bound)
    return False

def _shadowing_count(t, bound=()):
    if t[0] == 'l':
        return int(t[1] in bound) + _shadowing_count(t[2], bound + (t[1],))
    if t[0] == 'a':
        return _shadowing_count(t[1], bound) + _shadowing_count(t[2], bound)
    return 0

def _var_count(t, x):
    if t[0] == 'v': return int(t[1] == x)
    if t[0] == 'l': return 0 if t[1] == x else _var_count(t[2], x)
    return _var_count(t[1], x) + _var_count(t[2], x)

def _redexes(t, path=()):
    if t[0] == 'a':
        if t[1][0] == 'l': yield path, t
        yield from _redexes(t[1], path + (1,))
        yield from _redexes(t[2], path + (2,))
    elif t[0] == 'l':
        yield from _redexes(t[2], path + (2,))

def _lo_redex(t, path=()):
    if t[0] == 'a':
        if t[1][0] == 'l': return path, t
        out = _lo_redex(t[1], path + (1,))
        return out if out is not None else _lo_redex(t[2], path + (2,))
    if t[0] == 'l': return _lo_redex(t[2], path + (2,))
    return None

def _needs_alpha(body, x, arg):
    if body[0] == 'v': return False
    if body[0] == 'a':
        return _needs_alpha(body[1], x, arg) or _needs_alpha(body[2], x, arg)
    y, b = body[1], body[2]
    if y == x: return False
    return (y in _fv(arg) and x in _fv(b)) or _needs_alpha(b, x, arg)

def _alpha_renaming_redexes(t):
    return sum(_needs_alpha(r[1][2], r[1][1], r[2]) for _, r in _redexes(t))

def _capture_risk_redexes(t):
    return _alpha_renaming_redexes(t)

_BUCKETS = ('identity', 'dummy', 'substitution', 'duplication', 'shadowing',
            'alpha-renaming', 'deep-redex', 'root-redex', 'arbitrary')

def _phenomena(t):
    out = set()
    if _has_shadowing(t): out.add('shadowing')
    if _alpha_renaming_redexes(t): out.add('alpha-renaming')
    for path, r in _redexes(t):
        x, body = r[1][1], r[1][2]
        if not path: out.add('root-redex')
        else: out.add('deep-redex')
        if body == ('v', x): out.add('identity')
        elif x not in _fv(body): out.add('dummy')
        else:
            out.add('substitution')
            if _var_count(body, x) > 1: out.add('duplication')
    return out

def _contracted_phenomena(trace):
    out, counts = set(), Counter()
    for t in trace[:-1]:
        got = _lo_redex(t)
        if got is None: continue
        path, r = got
        x, body, arg = r[1][1], r[1][2], r[2]
        b = 'root-redex' if not path else 'deep-redex'
        out.add(b); counts[b] += 1
        if body == ('v', x):
            out.add('identity'); counts['identity'] += 1
        elif x not in _fv(body):
            out.add('dummy'); counts['dummy'] += 1
        else:
            out.add('substitution'); counts['substitution'] += 1
            if _var_count(body, x) > 1:
                out.add('duplication'); counts['duplication'] += 1
        if _needs_alpha(body, x, arg):
            out.add('alpha-renaming'); counts['alpha-renaming'] += 1
    return out, counts

def _split_key(t, nf):
    s = repr((_skeleton(t), _skeleton(nf))).encode()
    return hashlib.sha1(s).hexdigest()[:16]

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
        name = rng.choice(env) if env and rng.random() < 0.25 else f"v{len(env)}"
        return ('l', name, _gen_nf(depth - 1, rng, env + (name,)))
    head = ('v', rng.choice(env) if env and rng.random() < 0.7
                  else rng.choice(_LAM_CONSTS))
    n_args = 0 if depth <= 0 else rng.randint(0, 2)
    t = head
    for _ in range(n_args):
        t = ('a', t, _gen_nf(depth - 1, rng, env))
    return t

def _gen_term(depth, rng, env):
    if depth <= 0 or rng.random() < 0.25:
        return ('v', rng.choice(env) if env and rng.random() < 0.7 else rng.choice(_LAM_CONSTS))
    if depth > 2 and rng.random() < 0.25:
        x, y = f"v{len(env)}", f"v{len(env) + 1}"
        body = ('l', y, ('l', y, ('a', ('v', x), _gen_term(depth - 3, rng, env + (x, y, y)))))
        return ('a', ('l', x, body), ('v', y))
    if rng.random() < 0.35:
        name = rng.choice(env) if env and rng.random() < 0.3 else f"v{len(env)}"
        return ('l', name, _gen_term(depth - 1, rng, env + (name,)))
    if rng.random() < 0.25:
        x = f"v{len(env)}"
        return ('a', ('l', x, _gen_term(depth - 1, rng, env + (x,))),
                     _gen_term(depth - 1, rng, env))
    return ('a', _gen_term(depth - 1, rng, env), _gen_term(depth - 1, rng, env))

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

def _sample_by_antireduction(cfg, rng):
    nf = _gen_nf(cfg.nf_depth, rng, ())
    t = nf
    for _ in range(cfg.n_insertions):
        t2 = _insert_redex(t, rng, cfg.nf_depth)
        if len(_pretty(t2)) > cfg.max_chars: break
        t = t2
    return t, nf


@dataclass
class LambdaReductionConfig(Config):
    nf_depth: int = 5
    term_depth: int = 5
    n_insertions: int = 6
    min_steps: int = 5
    max_steps: int = 500
    max_chars: int = 500
    min_alpha_renaming: int = 1
    min_shadowing: int = 1
    anti_reduction_prob: float = 0.6

    def update(self, c=1):
        self.nf_depth += c
        self.term_depth += c
        self.n_insertions += c
        self.min_steps += c

    def apply_difficulty(self, level):
        self.nf_depth += level
        self.term_depth += level
        self.n_insertions += level
        self.min_steps += level


class LambdaReduction(Task):
    def __init__(self, config=None):
        super().__init__(config=config or LambdaReductionConfig())

    def generate(self):
        rng = random.Random()
        cfg = self.config
        source = 'anti_reduction' if rng.random() < cfg.anti_reduction_prob else 'arbitrary'
        target = rng.choice(_BUCKETS[:-1]) if source == 'anti_reduction' else 'arbitrary'
        for _ in range(3000):
            if source == 'anti_reduction':
                t, nf = _sample_by_antireduction(cfg, rng)
            else:
                t = _gen_term(cfg.term_depth, rng, ())

            if _term_size(t) > cfg.max_chars * 4: continue
            term = _pretty(t)
            if len(term) > cfg.max_chars: continue

            trace = _safe_normalize_trace(t, cfg.max_steps, cfg.max_chars * 4)
            if trace is None: continue
            if len(trace) - 1 < cfg.min_steps: continue
            if source == 'anti_reduction' and _debruijn(trace[-1]) != _debruijn(nf): continue
            nf, normal = trace[-1], _pretty(trace[-1])
            if not (3 <= len(normal) <= cfg.max_chars): continue
            if _step(nf) is not None: continue
            shadowing = _shadowing_count(t)
            syntactic_alpha_renaming = _alpha_renaming_redexes(t)
            syntactic_buckets = _phenomena(t)
            trace_buckets, trace_bucket_counts = _contracted_phenomena(trace)
            if shadowing:
                trace_buckets.add('shadowing')
            buckets = trace_buckets
            if target == 'shadowing' and shadowing < cfg.min_shadowing: continue
            if target == 'alpha-renaming' and trace_bucket_counts.get('alpha-renaming', 0) < cfg.min_alpha_renaming: continue
            if target != 'arbitrary' and target not in buckets: continue

            return Problem(
                metadata=edict(
                    term=term,
                    normal_form=normal,
                    beta_steps=len(trace) - 1,
                    has_shadowing=_has_shadowing(t),
                    shadowing=shadowing,
                    capture_risk=trace_bucket_counts.get('alpha-renaming', 0),
                    alpha_renaming=trace_bucket_counts.get('alpha-renaming', 0),
                    syntactic_alpha_renaming=syntactic_alpha_renaming,
                    skeleton=_skeleton(t),
                    nf_skeleton=_skeleton(nf),
                    split_key=_split_key(t, nf),
                    generator=source,
                    buckets=sorted(buckets),
                    syntactic_buckets=sorted(syntactic_buckets),
                    trace_bucket_counts=dict(trace_bucket_counts),
                    target_bucket=target,
                ),
                answer=normal,
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


def lambda_reduction_shortcut_report(train, test, predictions=None):
    """Diagnostics for splits and shortcut baselines; predictions are test-order or term-keyed."""
    train, test = list(train), list(test)
    def md(e): return e.metadata if hasattr(e, 'metadata') else edict(e['metadata'])
    def ans(e): return e.answer if hasattr(e, 'answer') else e['answer']
    def term(e): return _parse_lam(md(e).term)
    def sk(e, k):
        return repr(md(e).get(k) or _skeleton(term(e)))
    def score(p, e):
        try: return float(_debruijn(_parse_lam(str(p).strip())) == _debruijn(_parse_lam(ans(e))))
        except Exception: return 0.0
    def pred_for(i, e):
        if predictions is None: return None
        return predictions.get(md(e).term) if isinstance(predictions, dict) else predictions[i]
    def acc(items, f):
        items = list(items)
        return None if not items else sum(f(i, e) for i, e in items) / len(items)
    def root_only(t):
        for _ in range(500):
            if t[0] != 'a' or t[1][0] != 'l': return t
            t = _subst(t[1][2], t[1][1], t[2])
        return t
    def delete_wrappers(t):
        if t[0] == 'a' and t[1][0] == 'l' and t[1][1] not in _fv(t[1][2]):
            return delete_wrappers(t[1][2])
        if t[0] == 'a': return ('a', delete_wrappers(t[1]), delete_wrappers(t[2]))
        if t[0] == 'l': return ('l', t[1], delete_wrappers(t[2]))
        return t

    train_pairs = {(md(e).term, ans(e)) for e in train}
    train_in_skel = {sk(e, 'skeleton') for e in train}
    train_nf_skel = {sk(e, 'nf_skeleton') for e in train}
    all_items = list(train) + list(test)
    source_counts = Counter(md(e).get('generator', 'unknown') for e in all_items)
    indexed = list(enumerate(test))
    lm_acc = None if predictions is None else acc(indexed, lambda i, e: score(pred_for(i, e), e))
    by_steps = {}
    if predictions is not None:
        for s in sorted({md(e).beta_steps for e in test if 'beta_steps' in md(e)}):
            by_steps[str(s)] = acc(((i, e) for i, e in indexed if md(e).get('beta_steps') == s),
                                   lambda i, e: score(pred_for(i, e), e))
    return edict(
        exact_train_test_duplicate_rate=sum((md(e).term, ans(e)) in train_pairs for e in test) / len(test),
        input_skeleton_overlap=sum(sk(e, 'skeleton') in train_in_skel for e in test) / len(test),
        normal_form_skeleton_overlap=sum(sk(e, 'nf_skeleton') in train_nf_skel for e in test) / len(test),
        accepted_generator_ratio={k: v / len(all_items) for k, v in source_counts.items()},
        one_step_contraction_baseline=acc(indexed, lambda i, e: score(_pretty(_step(term(e)) or term(e)), e)),
        root_redex_only_baseline=acc(indexed, lambda i, e: score(_pretty(root_only(term(e))), e)),
        delete_wrapper_baseline=acc(indexed, lambda i, e: score(_pretty(delete_wrappers(term(e))), e)),
        tuned_accuracy=lm_acc,
        tuned_accuracy_by_beta_steps=by_steps or None,
        tuned_capture_risk_accuracy=None if predictions is None else acc(
            ((i, e) for i, e in indexed if md(e).get('capture_risk', 0)),
            lambda i, e: score(pred_for(i, e), e)),
        tuned_ood_steps_accuracy=None if predictions is None else acc(
            ((i, e) for i, e in indexed if md(e).get('beta_steps', 0) >= 8),
            lambda i, e: score(pred_for(i, e), e)),
        tuned_unseen_skeleton_accuracy=None if predictions is None else acc(
            ((i, e) for i, e in indexed if sk(e, 'skeleton') not in train_in_skel),
            lambda i, e: score(pred_for(i, e), e)),
        tuned_arbitrary_generator_accuracy=None if predictions is None else acc(
            ((i, e) for i, e in indexed if md(e).get('generator') == 'arbitrary'),
            lambda i, e: score(pred_for(i, e), e)),
        tuned_alpha_renaming_required_accuracy=None if predictions is None else acc(
            ((i, e) for i, e in indexed if md(e).get('alpha_renaming', md(e).get('capture_risk', 0))),
            lambda i, e: score(pred_for(i, e), e)),
        tuned_duplication_accuracy=None if predictions is None else acc(
            ((i, e) for i, e in indexed if 'duplication' in md(e).get('buckets', ())),
            lambda i, e: score(pred_for(i, e), e)),
    )








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

    def apply_difficulty(self, level):
        self.depth += level
        self.n_insertions += level
        self.max_rules = min(self.max_rules + level, 12)
        self.min_steps += level
        self.max_steps += 50 * level
        self.max_chars += 120 * level
        self.atom_keep_prob = max(0.35, self.atom_keep_prob - 0.05 * level)
        self.shortcut_compression = max(8.0, self.shortcut_compression - 2.0 * level)


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
