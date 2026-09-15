import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'robdd_reduction_trace (draw 2 of 3)',
 'hypothesis': 'P009',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/robdd_reduction_trace',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2701974858,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}

_VARS = ['x', 'y', 'z', 'u', 'v', 'w', 'p', 'q']


def _tokenize(expr):
    tokens = []
    i = 0
    while i < len(expr):
        c = expr[i]
        if c.isspace():
            i += 1
            continue
        if c in '(),':
            tokens.append(c)
            i += 1
            continue
        if c.isalpha():
            j = i
            while j < len(expr) and expr[j].isalpha():
                j += 1
            tokens.append(expr[i:j])
            i = j
            continue
        if c.isdigit():
            j = i
            while j < len(expr) and expr[j].isdigit():
                j += 1
            tokens.append(int(expr[i:j]))
            i = j
            continue
        raise ValueError(expr)
    return tokens


def _parse_expr(expr, var_subs=None):
    var_subs = var_subs or {}
    tokens = _tokenize(expr)

    idx = {'i': 0}

    def peek():
        return tokens[idx['i']] if idx['i'] < len(tokens) else None

    def pop():
        t = tokens[idx['i']]
        idx['i'] += 1
        return t

    def parse_or():
        left = parse_and()
        while peek() == 'or':
            pop()
            right = parse_and()
            left = ('or', left, right)
        return left

    def parse_and():
        left = parse_primary()
        while peek() == 'and':
            pop()
            right = parse_primary()
            left = ('and', left, right)
        return left

    def parse_primary():
        t = peek()
        if t == '(':
            pop()
            node = parse_or()
            if peek() != ')':
                raise ValueError(expr)
            pop()
            return node
        if t == 'not':
            pop()
            return ('not', parse_primary())
        if isinstance(t, int):
            pop()
            return t
        if isinstance(t, str) and t.isalpha():
            pop()
            return var_subs.get(t, t)
        raise ValueError(repr(t))

    node = parse_or()
    if idx['i'] != len(tokens):
        raise ValueError(expr)
    return node


def _eval_node(node, assignment):
    if node in (0, 1):
        return node
    if isinstance(node, str):
        return assignment[node]
    op = node[0]
    if op == 'not':
        return 1 - _eval_node(node[1], assignment)
    if op == 'and':
        return _eval_node(node[1], assignment) & _eval_node(node[2], assignment)
    if op == 'or':
        return _eval_node(node[1], assignment) | _eval_node(node[2], assignment)
    raise ValueError(node)


def _node_vars(node, out):
    if node in (0, 1):
        return
    if isinstance(node, str):
        out.add(node)
        return
    for child in node[1:]:
        _node_vars(child, out)


def _truth_table(node, order):
    vars_list = list(order)
    n = len(vars_list)
    rows = []
    for mask in range(1 << n):
        assignment = {}
        for j, v in enumerate(vars_list):
            assignment[v] = (mask >> (n - 1 - j)) & 1
        rows.append(_eval_node(node, assignment))
    return rows


def _eval_ite(ite_str, order, mask):
    n = len(order)
    assignment = {}
    for j, v in enumerate(order):
        assignment[v] = (mask >> (n - 1 - j)) & 1

    tokens = _tokenize(ite_str)
    idx = {'i': 0}

    def peek():
        return tokens[idx['i']] if idx['i'] < len(tokens) else None

    def pop():
        t = tokens[idx['i']]
        idx['i'] += 1
        return t

    def parse():
        t = pop()
        if t == 'ite':
            pop()
            var = pop()
            pop()
            hi = parse()
            pop()
            lo = parse()
            pop()
            return hi if assignment[var] else lo
        if t in (0, 1):
            return t
        if isinstance(t, str) and t.isalpha():
            return assignment[t]
        raise ValueError(repr(t))

    result = parse()
    if idx['i'] != len(tokens):
        raise ValueError(ite_str)
    return result


def _build_robdd(order, truth_rows):
    n = len(order)
    memo = {}

    def build(index, mask):
        key = (index, mask)
        if key in memo:
            return memo[key]
        if index == n:
            memo[key] = '1' if truth_rows[mask] else '0'
            return memo[key]
        v = order[index]
        bit = n - 1 - index
        hi_mask = mask | (1 << bit)
        lo_mask = mask & ~(1 << bit)
        hi = build(index + 1, hi_mask)
        lo = build(index + 1, lo_mask)
        if hi == lo:
            res = hi
        else:
            res = 'ite(%s, %s, %s)' % (v, hi, lo)
        memo[key] = res
        return res

    return build(0, 0)


def _render_expr(node):
    if node == 0:
        return '0'
    if node == 1:
        return '1'
    if isinstance(node, str):
        return node
    op = node[0]
    if op == 'not':
        return 'not (' + _render_expr(node[1]) + ')'
    return '(' + _render_expr(node[1]) + ' ' + op + ' ' + _render_expr(node[2]) + ')'


@dataclass
class RobddConfig(Config):
    n_vars: int = 3
    max_depth: int = 4

    def apply_difficulty(self, level):
        self.n_vars = 2 + min(4, level)
        self.max_depth = 3 + level


class RobddReductionTrace(Task):
    summary = ("Construct the reduced ordered BDD of a small boolean function under a fixed "
               "variable order by Shannon cofactoring and isomorphic-node merging; answer the "
               "canonical serialized ITE structure.")
    design_choice = ("Answer as a canonical serialized ITE string (e.g., ite(x1, ite(x2,0,1), 1)) "
                     "of the reduced BDD, with the function given as a Boolean expression.")
    config_cls = RobddConfig
    task_version = 2

    def _gen_expr(self, vars_list, max_depth):
        if max_depth <= 0:
            r = random.random()
            if r < 0.75:
                return random.choice(vars_list)
            return random.randint(0, 1)
        r = random.random()
        op = random.choice(['and', 'or', 'not'])
        if op == 'not':
            return ('not', self._gen_expr(vars_list, max_depth - 1))
        left = self._gen_expr(vars_list, max_depth - 1)
        right = self._gen_expr(vars_list, max_depth - 1)
        return (op, left, right)

    def generate_entry(self):
        n = self.config.n_vars
        vars_list = _VARS[:n]
        order = list(vars_list)
        for _ in range(1000):
            node = self._gen_expr(vars_list, self.config.max_depth)
            expr_str = _render_expr(node)
            reparse = _parse_expr(expr_str)
            if reparse != node:
                continue
            tt = _truth_table(node, order)
            if len(set(tt)) == 1:
                continue
            answer = _build_robdd(order, tt)
            ok = True
            try:
                for mask in range(1 << n):
                    if _eval_ite(answer, order, mask) != tt[mask]:
                        ok = False
                        break
            except Exception:
                ok = False
            if ok:
                break
        else:
            raise RuntimeError('failed to generate valid ROBDD')
        metadata = {
            'order': order,
            'expr': expr_str,
            'truth_table': tt,
        }
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        return (
            "For the boolean function below, build the reduced ordered binary decision diagram "
            "(ROBDD) under the fixed variable order and write the canonical serialized ITE "
            "structure. In ITE form, ite(v, hi, lo) means: if v then hi else lo, from Shannon "
            "cofactoring with isomorphic subtrees merged and nodes eliminated when their two "
            "children are identical.\n"
            "Function: %s. Variable order: %s.\n"
            "Answer with only the serialized ITE structure of the reduced BDD, using 0 for false "
            "and 1 for true. For example, ite(x, ite(y, 0, 1), 1)."
            % (metadata['expr'], ', '.join(metadata['order']))
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        norm = re.sub(r'\s+', '', answer)
        gold = re.sub(r'\s+', '', entry.answer)
        return 1.0 if norm == gold else 0.0
