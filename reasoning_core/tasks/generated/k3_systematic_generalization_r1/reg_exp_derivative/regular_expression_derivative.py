import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'regular_expression_derivative (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_systematic_generalization_r1/regular_expression_derivative',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1662004003,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

ALPHABET = ('a', 'b')
EMPTY = ('empty',)
EPS = ('eps',)


def _leaf():
    r = random.random()
    if r < 0.06:
        return EMPTY
    if r < 0.07:
        return EPS
    return random.choice(ALPHABET)


def _gen(depth):
    if depth <= 0:
        return _leaf()
    op = random.choices(
        ['union', 'cat', 'star', 'leaf'],
        weights=[2, 8, 1, 1],
    )[0]
    if op == 'leaf':
        return _leaf()
    if op == 'star':
        return ('star', _gen(depth - 1))
    left = _gen(depth - random.randint(1, 2))
    right = _gen(depth - random.randint(1, 2))
    return (op, left, right)


def _nullable(e):
    if e == EMPTY:
        return False
    if e == EPS:
        return True
    if isinstance(e, str):
        return False
    if e[0] == 'union':
        return _nullable(e[1]) or _nullable(e[2])
    if e[0] == 'cat':
        return _nullable(e[1]) and _nullable(e[2])
    if e[0] == 'star':
        return True
    return False


def _simplify(e):
    if isinstance(e, str) or e == EMPTY or e == EPS:
        return e
    op = e[0]
    if op == 'star':
        inner = _simplify(e[1])
        if inner == EMPTY or inner == EPS:
            return EPS
        return ('star', inner)
    if op == 'union':
        a = _simplify(e[1])
        b = _simplify(e[2])
        if a == EMPTY:
            return b
        if b == EMPTY:
            return a
        if a == b:
            return a
        return ('union', a, b)
    if op == 'cat':
        a = _simplify(e[1])
        b = _simplify(e[2])
        if a == EMPTY or b == EMPTY:
            return EMPTY
        if a == EPS:
            return b
        if b == EPS:
            return a
        return ('cat', a, b)
    return e


def _deriv(ch, e):
    if e == EMPTY or e == EPS or isinstance(e, str):
        if isinstance(e, str):
            return EPS if e == ch else EMPTY
        return EMPTY
    op = e[0]
    if op == 'union':
        return _simplify(('union', _deriv(ch, e[1]), _deriv(ch, e[2])))
    if op == 'star':
        return _simplify(('cat', _deriv(ch, e[1]), ('star', e[1])))
    if op == 'cat':
        da = _simplify(('cat', _deriv(ch, e[1]), e[2]))
        if _nullable(e[1]):
            da = _simplify(('union', da, _deriv(ch, e[2])))
        return _simplify(da)
    return e


def _matches(e, w):
    if e == EMPTY:
        return False
    if e == EPS:
        return len(w) == 0
    if isinstance(e, str):
        return w == e
    op = e[0]
    if op == 'union':
        return _matches(e[1], w) or _matches(e[2], w)
    if op == 'cat':
        return any(_matches(e[1], w[:i]) and _matches(e[2], w[i:])
                   for i in range(len(w) + 1))
    if op == 'star':
        return _star(e[1], w)
    return False


def _star(inner, w):
    if len(w) == 0:
        return True
    for i in range(1, len(w) + 1):
        if _matches(inner, w[:i]) and _star(inner, w[i:]):
            return True
    return False


def _all_words(maxlen):
    out = ['']
    for n in range(1, maxlen + 1):
        frontier = ['']
        for _ in range(n):
            nxt = []
            for p in frontier:
                nxt.append(p + 'a')
                nxt.append(p + 'b')
            frontier = nxt
        out.extend(frontier)
    return out


def _is_reduced(e):
    if isinstance(e, str) or e == EMPTY or e == EPS:
        return True
    op = e[0]
    if op == 'star':
        return _is_reduced(e[1]) and e[1] != EMPTY and e[1] != EPS
    if op == 'union':
        return (_is_reduced(e[1]) and _is_reduced(e[2])
                and e[1] != EMPTY and e[2] != EMPTY and e[1] != e[2])
    if op == 'cat':
        return (_is_reduced(e[1]) and _is_reduced(e[2])
                and e[1] != EMPTY and e[2] != EMPTY
                and e[1] != EPS and e[2] != EPS)
    return False


def _verify(ch, expr, deriv):
    words = _all_words(6)
    for w in words:
        lhs = _matches(deriv, w)
        rhs = _matches(expr, ch + w)
        if lhs != rhs:
            return False
    if not _is_reduced(deriv):
        return False
    return True


def _render(e):
    if e == EMPTY:
        return '0'
    if e == EPS:
        return '1'
    if isinstance(e, str):
        return e
    op = e[0]
    if op == 'star':
        inner = _render(e[1])
        if _is_atom(e[1]):
            return inner + '*'
        return '(' + inner + ')*'
    if op == 'union':
        return '(' + _render(e[1]) + ' U ' + _render(e[2]) + ')'
    if op == 'cat':
        return '(' + _render(e[1]) + ' ' + _render(e[2]) + ')'
    return ''


def _is_atom(e):
    return isinstance(e, str) or e == EMPTY or e == EPS


@dataclass
class RegExpDerivativeConfig(Config):
    depth: int = 4

    def apply_difficulty(self, level):
        self.depth = 4 + level


class RegExpDerivative(Task):
    summary = "Compute Brzozowski derivatives of small regular expressions over {a,b} with respect to one symbol, simplifying nullable subexpressions via the empty/epsilon/union/concat/star identity laws, returning the fully simplified derivative expression, or the boolean true when the derivative is nullable."
    config_cls = RegExpDerivativeConfig
    design_choice = "Derivative answer form: return the fully simplified derivative expression string, or if nullable, return the boolean true/false instead of the expression."

    def generate_entry(self):
        depth = self.config.depth
        while True:
            expr = _simplify(_gen(depth))
            if expr == EMPTY or expr == EPS:
                continue
            ch = random.choice(ALPHABET)
            d = _simplify(_deriv(ch, expr))
            if d == EMPTY:
                continue
            if not _verify(ch, expr, d):
                continue
            nullable = _nullable(d)
            if nullable:
                answer = 'true'
            else:
                answer = _render(d)
            return Entry(metadata={
                'expression': _render(expr),
                'symbol': ch,
                'derivative': _render(d),
                'nullable': nullable,
            }, answer=answer)

    def render_prompt(self, metadata):
        ch = metadata['symbol']
        return (f"Let R = {metadata['expression']} be a regular expression over the "
                f"alphabet (a, b), where 1 denotes the empty string and 0 the empty set. "
                f"Using Brzozowski derivatives, compute the (left) derivative of R with "
                f"respect to the symbol '{ch}', then simplify the result with the identity "
                f"laws. If the simplified derivative is nullable (accepts the empty string), "
                f"answer exactly true; otherwise answer the fully simplified derivative "
                f"expression, writing 1 for the empty string, 0 for the empty set, U for "
                f"union, juxtaposition for concatenation, and * for star.")

    def score_answer(self, answer, entry):
        return 1.0 if answer == entry.answer else 0.0
