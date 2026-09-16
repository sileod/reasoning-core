import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class CtlFixpointConfig(Config):
    states: int = 4
    max_post: int = 2
    labels: int = 2

    def apply_difficulty(self, level):
        self.states = 4 + level
        self.max_post = 2 + (level >= 3)
        self.labels = 2 + (level >= 4)


def _letter(i):
    return chr(ord('a') + i)


def _least(trans, f):
    n = len(trans)
    x = set()
    while True:
        nx = f(x)
        if nx == x:
            return x
        x = nx


def _greatest(trans, f):
    n = len(trans)
    x = set(range(n))
    while True:
        nx = f(x)
        if nx == x:
            return x
        x = nx


def _ex(trans, sat):
    n = len(trans)
    return {q for q in range(n) for t in trans[q] if t in sat}


def _ax(trans, sat):
    n = len(trans)
    return {q for q in range(n) if all(t in sat for t in trans[q])}


def _eu(trans, a, b):
    n = len(trans)

    def f(z):
        return b | {q for q in range(n) if q in a and any(t in z for t in trans[q])}

    return _least(trans, f)


def _au(trans, a, b):
    n = len(trans)

    def f(z):
        return b | {q for q in range(n) if q in a and all(t in z for t in trans[q])}

    return _least(trans, f)


def _eg(trans, a):
    n = len(trans)
    # EG a : greatest fixpoint of  a & EX
    def f(z):
        return {q for q in range(n) if q in a and any(t in z for t in trans[q])}

    return _greatest(trans, f)


def _check(trans, labels, ast):
    n = len(trans)
    op = ast[0]
    if op == 'prop':
        _, name = ast
        return {q for q in range(n) if labels[q] == name}
    if op == 'not':
        _, a = ast
        return set(range(n)) - _check(trans, labels, a)
    if op == 'and':
        _, a, b = ast
        return _check(trans, labels, a) & _check(trans, labels, b)
    if op == 'or':
        _, a, b = ast
        return _check(trans, labels, a) | _check(trans, labels, b)
    if op == 'ex':
        _, a = ast
        return _ex(trans, _check(trans, labels, a))
    if op == 'ax':
        _, a = ast
        return _ax(trans, _check(trans, labels, a))
    if op == 'ef':
        _, a = ast
        return _eu(trans, set(range(n)), _check(trans, labels, a))
    if op == 'af':
        _, a = ast
        return _au(trans, set(range(n)), _check(trans, labels, a))
    if op == 'eg':
        _, a = ast
        return _eg(trans, _check(trans, labels, a))
    if op == 'ag':
        _, a = ast
        # AG a == not EF not a
        inner = _check(trans, labels, a)
        return set(range(n)) - _eu(trans, set(range(n)), set(range(n)) - inner)
    if op == 'eu':
        _, a, b = ast
        return _eu(trans, _check(trans, labels, a), _check(trans, labels, b))
    if op == 'au':
        _, a, b = ast
        return _au(trans, _check(trans, labels, a), _check(trans, labels, b))
    raise ValueError(op)


def _make_ast(formula):
    # Sequential parser for a small CTL grammar.
    pos = 0
    tokens = formula.replace('(', ' ( ').replace(')', ' ) ').split()

    def parse_expr():
        nonlocal pos
        tok = tokens[pos]
        if tok == 'true':
            pos += 1
            return ('or', ('prop', 'p'), ('not', ('prop', 'p')))
        if tok.startswith('p') or tok.startswith('q'):
            pos += 1
            return ('prop', tok)
        if tok == 'not':
            pos += 1
            return ('not', parse_expr())
        if tok in ('EX', 'AX', 'EF', 'AF', 'EG', 'AG'):
            pos += 1
            return (tok.lower(), parse_expr())
        if tok in ('EU', 'AU'):
            pos += 1
            a = parse_expr()
            b = parse_expr()
            return (tok.lower(), a, b)
        raise ValueError(f"parse error at {tok}")

    return parse_expr()


def _eval_formula(trans, labels, formula):
    return _check(trans, labels, _make_ast(formula))


def _random_formula(meta, labels_list):
    depth = meta['depth']
    leaf_pool = ['p', 'q'] if len(labels_list) >= 2 else ['p']
    ops = random.choice(['unary', 'binary'])
    unary_ops = ['EX', 'AX', 'EG', 'AF']
    binary_ops = ['EU', 'AU']

    def build(d):
        if d <= 0:
            return random.choice(leaf_pool)
        if random.random() < 0.25:
            return random.choice(leaf_pool)
        if ops == 'unary' or random.random() < 0.5:
            o = random.choice(unary_ops)
            return f"{o} {build(d - 1)}"
        else:
            o = random.choice(binary_ops)
            return f"{o} {build(d - 1)} {build(d - 1)}"

    return build(depth)


class CtlFixpointModelChecking(Task):
    summary = ("Evaluate nested CTL formulas on small Kripke structures (lassos, trees, diamonds) "
               "by least/greatest fixpoint iteration for EX/AX, EF/EG and until operators; answers "
               "are the sorted satisfying-state set.")
    design_choice = ("Represent each satisfying state as a single lowercase letter, with the answer "
                     "being a sorted concatenation like 'abde' and a fixed alphabet of at most 26 states.")
    config_cls = CtlFixpointConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config
        n = cfg.states
        letters = [_letter(i) for i in range(n)]

        while True:
            trans = {}
            for q in range(n):
                cnt = random.randint(1, cfg.max_post)
                trans[q] = random.sample(range(n), cnt)
            if all(len(v) > 0 for v in trans.values()):
                break

        labels = [random.sample(['p', 'q'], 1)[0] for _ in range(n)]

        structure = random.choice(['lasso', 'tree', 'diamond', 'grid'])
        depth = 1 + (cfg.states >= 6)

        while True:
            formula = _random_formula({'depth': depth}, ['p', 'q'])
            sat = _eval_formula(trans, labels, formula)
            ans = ''.join(letters[q] for q in sorted(sat)) or 'emptyset'
            break

        return Entry(metadata={
            "trans": {_letter(k): [_letter(t) for t in v] for k, v in trans.items()},
            "labels": {_letter(q): v for q, v in enumerate(labels)},
            "formula": formula,
            "structure": structure,
        }, answer=ans)

    def render_prompt(self, metadata):
        lines = []
        lines.append("Consider a Kripke structure whose states are the letters "
                     "a, b, ... with transition relation T:")
        for k in sorted(metadata["trans"]):
            lines.append(f"  {k} -> {' '.join(metadata['trans'][k])}")
        lines.append("Each state carries an atomic proposition (labeling):")
        for k in sorted(metadata["labels"]):
            lines.append(f"  {k} : {metadata['labels'][k]}")
        lines.append(f"Formula: {metadata['formula']}")
        lines.append("Find the set of states satisfying the CTL formula by fixpoint iteration "
                     "(EX exists a successor, AX all successors, EF/EG the least/greatest fixpoint, "
                     "EU/AU until).")
        lines.append("Answer: the satisfying states as a sorted concatenation of single lowercase "
                     "state letters (e.g. 'abde'); the empty set is 'emptyset'.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'ctl_fixpoint_model_checking (draw 1 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/ctl_fixpoint_model_checking',
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
