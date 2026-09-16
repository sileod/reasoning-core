import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'symbolic_differentiation (draw 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/symbolic_differentiation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1336314872,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

SINGLE = ['exp', 'ln', 'sin', 'cos', 'tan']
BINARY = ['add', 'sub', 'mul', 'div', 'pow']


def render(node):
    if isinstance(node, tuple):
        op = node[0]
        k = node[1]
        if op in SINGLE:
            name = {'exp': 'e^', 'ln': 'ln', 'sin': 'sin', 'cos': 'cos', 'tan': 'tan'}[op]
            return "%s(%s)" % (name, render(k[0]))
        if op == 'pow':
            return "((%s)^(%s))" % (render(k[0]), render(k[1]))
        if op == 'mul':
            return "((%s)*(%s))" % (render(k[0]), render(k[1]))
        if op == 'div':
            return "((%s)/(%s))" % (render(k[0]), render(k[1]))
        if op == 'add':
            return "((%s)+(%s))" % (render(k[0]), render(k[1]))
        if op == 'sub':
            return "((%s)-(%s))" % (render(k[0]), render(k[1]))
    return str(node)


def render_tree(node):
    if isinstance(node, tuple):
        kids = ", ".join(render_tree(k) for k in node[1])
        return "(%s,[%s])" % (node[0], kids)
    return str(node)


def deriv(node):
    if isinstance(node, str):
        return 1 if node == 'x' else 0
    if isinstance(node, int):
        return 0
    op = node[0]
    k = node[1]
    if op == 'add':
        return ('add', [deriv(k[0]), deriv(k[1])])
    if op == 'sub':
        return ('sub', [deriv(k[0]), deriv(k[1])])
    if op == 'mul':
        return ('add', [('mul', [deriv(k[0]), k[1]]), ('mul', [k[0], deriv(k[1])])])
    if op == 'div':
        num = ('sub', [('mul', [deriv(k[0]), k[1]]), ('mul', [k[0], deriv(k[1])])])
        return ('div', [num, ('pow', [k[1], 2])])
    if op == 'pow':
        base, nexp = k
        return ('mul', [('mul', [nexp, ('pow', [base, ('sub', [nexp, 1])])]), deriv(base)])
    if op == 'exp':
        return ('mul', [('exp', [k[0]]), deriv(k[0])])
    if op == 'ln':
        return ('div', [deriv(k[0]), k[0]])
    if op == 'sin':
        return ('mul', [('cos', [k[0]]), deriv(k[0])])
    if op == 'cos':
        return ('mul', [('mul', [-1, ('sin', [k[0]])]), deriv(k[0])])
    if op == 'tan':
        return ('mul', [('div', [1, ('pow', [('cos', [k[0]]), 2])]), deriv(k[0])])
    raise ValueError(op)


@dataclass
class DiffConfig(Config):
    depth: int = 2

    def apply_difficulty(self, level):
        self.depth = 1 + level


class SymbolicDifferentiation(Task):
    summary = ("Differentiate expression trees over sums, products, quotients, powers, and "
               "elementary functions via recursive product, quotient, and chain rules, nesting "
               "compositions several levels; answer is the rule-ordered derivative.")
    design_choice = ("Choice 2: Provide the expression tree as a nested list of nodes "
                     "(operator, children); the solver outputs the derivative as a nested list, "
                     "preserving rule order without simplification.")
    config_cls = DiffConfig

    def _node(self, depth):
        if depth <= 0:
            return 'x' if random.random() < 0.5 else random.randint(2, 9)
        r = random.random()
        if r < 0.2:
            return 'x' if random.random() < 0.5 else random.randint(2, 9)
        op = random.choice(OPS)
        order = 2 if op in BINARY else 1
        if op == 'pow':
            base = self._node(depth - 1)
            nexp = random.randint(1, 5)
            return (op, [base, nexp])
        ks = [self._node(depth - 1) for _ in range(order)]
        return (op, ks)

    def generate_entry(self):
        tree = self._node(self.config.depth)
        d = deriv(tree)
        return Entry(metadata={'tree': render_tree(tree), 'rules': 'product/quotient/chain'},
                     answer=render_tree(d))

    def render_prompt(self, metadata):
        return (f"Let f = {metadata['tree']}. This convex nested tuple encodes an expression "
                f"tree: each node is (operator, [children]) where 'x' and integers are leaves. "
                f"Operators: add, sub, mul, div, pow, exp, ln, sin, cos, tan. Using the product "
                f"rule, quotient rule, and chain rule recursively, compute the derivative f' and "
                f"encode it as the SAME nested-tuple format, WITHOUT simplifying, expanding, or "
                f"combining any subexpressions. Preserve the rule order of the derivative. "
                f"Example: for (add,[x,3]) the answer is (add,[1,0]); for (mul,[x,3]) it is "
                f"(add,[(mul,[1,3]),(mul,[x,0])]). Give only the derivative nested tuple.")

    def score_answer(self, answer, entry):
        gold = entry.answer
        return 1.0 if answer.strip() == gold else 0.0


OPS = SINGLE + BINARY
