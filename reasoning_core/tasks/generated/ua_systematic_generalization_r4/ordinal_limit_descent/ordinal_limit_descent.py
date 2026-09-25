import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'ordinal_limit_descent (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_systematic_generalization_r4/ordinal_limit_descent',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
                                         'version': 'bubblewrap 0.8.0'}}}}

# An ordinal below epsilon-0 is a Cantor normal form: an ordered tuple of
# (exponent, coeff) pairs, exponents strictly decreasing, each exponent itself
# such a tuple, each coeff a positive integer.  Zero is the empty tuple.


def _cmp(a, b):
    if a == b:
        return 0
    i = 0
    while i < len(a) and i < len(b):
        ea, ca = a[i]
        eb, cb = b[i]
        c = _cmp(ea, eb)
        if c != 0:
            return c
        if ca != cb:
            return 1 if ca > cb else -1
        i += 1
    return 1 if len(a) > len(b) else -1


def _add(a, b):
    if not a:
        return b
    if not b:
        return a
    a = list(a)
    b = list(b)
    out = []
    ia = ib = 0
    while ia < len(a) and ib < len(b):
        ea, ca = a[ia]
        eb, cb = b[ib]
        c = _cmp(ea, eb)
        if c > 0:
            out.append((ea, ca))
            ia += 1
        elif c < 0:
            out.append((eb, cb))
            ib += 1
        else:
            cs = ca + cb
            if cs:
                out.append((ea, cs))
            ia += 1
            ib += 1
    out.extend(a[ia:])
    out.extend(b[ib:])
    return tuple(out)


def _mono(exp, coeff):
    return ((exp, coeff),)


def _predecessor(o):
    if not o:
        return None
    e, c = o[-1]
    if e != ():
        return None
    if c >= 2:
        return _add(o[:-1], _mono((), c - 1))
    return o[:-1]


def _fund_of_power(e, n):
    pred = _predecessor(e)
    if pred is not None:
        return _mono(pred, n)
    return _mono(_fund_seq(e, n), 1)


def _fund_seq(o, n):
    lead = o[:-1]
    e, c = o[-1]
    piece = _fund_of_power(e, n)
    if c >= 2:
        return _add(_add(lead, _mono(e, c - 1)), piece)
    return _add(lead, piece)


def _descent(o, n):
    pred = _predecessor(o)
    if pred is not None:
        return pred
    return _fund_seq(o, n)


def _term_str(term):
    e, c = term
    if e == ():
        return str(c)
    s = "w^(" + _ord_str(e) + ")"
    if c > 1:
        s = s + "*" + str(c)
    return s


def _ord_str(o):
    if not o:
        return "0"
    return "+".join(_term_str(t) for t in o)


def _rand_ordinal(depth, max_coeff, max_terms):
    if depth <= 1:
        return _mono((), random.randint(1, max_coeff))
    nterms = random.randint(1, max_terms)
    terms = []
    upper = None
    for _ in range(nterms):
        exp = None
        for _r in range(40):
            if random.random() < 0.7:
                cand = _rand_ordinal(depth - 1, max_coeff, max_terms)
            else:
                cand = _mono((), random.randint(1, max_coeff))
            if upper is None or _cmp(cand, upper) < 0:
                exp = cand
                break
        if exp is None:
            break
        terms.append((exp, random.randint(1, max_coeff)))
        upper = exp
    if not terms:
        return _mono((), random.randint(1, max_coeff))
    return tuple(terms)


def _gen_ordinal(depth, max_coeff, max_terms):
    power = _rand_ordinal(depth, max_coeff, max_terms)
    if random.random() < 0.45:
        return _add(power, _mono((), random.randint(1, max_coeff)))
    return power


@dataclass
class OrdinalLimitDescentConfig(Config):
    depth: int = 2
    max_coeff: int = 4
    max_terms: int = 2

    def apply_difficulty(self, level):
        self.depth = 2 + (level // 3)
        self.max_coeff = 3 + level
        self.max_terms = 2 + (level // 2)


class OrdinalLimitDescent(Task):
    summary = ("Execute indexed descents on ordinals below epsilon-zero: subtract at "
               "successors and apply stated fundamental sequences at limits, recursively "
               "handling sums and nested powers; return the residual ordinal.")
    design_choice = ("Represent the target ordinal in Cantor normal form with coefficients "
                     "as ordinals, and require the solver to fully normalize the residual "
                     "after each descent step.")
    config_cls = OrdinalLimitDescentConfig
    task_version = 2

    def generate_entry(self):
        for _ in range(200):
            alpha = _gen_ordinal(self.config.depth, self.config.max_coeff,
                                 self.config.max_terms)
            successor = _predecessor(alpha) is not None
            n = random.randint(1, self.config.max_coeff)
            residual = _descent(alpha, n)
            if residual is None or residual == ():
                continue
            mode = "successor" if successor else "limit"
            if _cmp(residual, alpha) >= 0:
                continue
            return Entry(metadata={
                "alpha": _ord_str(alpha),
                "n": n,
                "mode": mode,
                "residual": _ord_str(residual),
            }, answer=_ord_str(residual))
        raise RuntimeError("ordinal_limit_descent: failed to generate an instance")

    def render_prompt(self, metadata):
        return (
            "We work with ordinals below epsilon-zero in Cantor normal form. Notation: "
            "w is the first infinite ordinal, w^(e) is a nested power with exponent "
            "e itself an ordinal, t*c multiplies a term by a positive integer c, and a "
            "sum a+b is written with exponents strictly decreasing, so "
            "w^(w)*2 means w^(w)+w^(w), and w^(1)*3 means w^(1)+w^(1)+w^(1).\n"
            "A single descent step on an ordinal a with an index n (a positive integer) is:\n"
            "- if a is a successor ordinal (it ends with a positive natural term), subtract 1;\n"
            "- if a is a limit ordinal (no natural term), apply its n-th fundamental-sequence "
            "element: descend the least (rightmost) term of the Cantor normal form, where "
            "w^((b+1))*c becomes w^((b+1))*(c-1)+w^(b)*n and w^(l) becomes w^(l[n]) for a limit "
            "exponent l, recursing into sums and nested powers.\n"
            "Fully normalize the residual to Cantor normal form.\n\n"
            f"Given a = {metadata['alpha']} and index n = {metadata['n']}, what is the "
            "residual ordinal after one descent step? Answer with the normalized ordinal "
            "only, using the notation above."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == entry["answer"] else 0.0

    def distractor_candidates(self, entry):
        n = entry["n"]
        yield entry["alpha"]
        yield _ord_str(_mono((), n))
        yield _ord_str(_fund_of_power(_mono((), 1), n)) if entry["mode"] == "limit" else entry["alpha"]
