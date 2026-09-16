import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround


@dataclass
class CayleyEvalConfig(Config):
    n_min: int = 4
    n_max: int = 4
    max_leaves: int = 3
    max_occs: int = 2
    max_attempts: int = 300

    def apply_difficulty(self, level):
        self.n_max = self.n_min + sround(1.0 * level)
        self.max_leaves = 3 + sround(1.0 * level)
        self.max_occs = 2 + sround(0.8 * level)
        self.max_attempts = 300 + 60 * level


def _rand_table(n):
    return [[random.randrange(n) for _ in range(n)] for _ in range(n)]


def _table_with_identity_absorbing(n):
    for _ in range(200):
        cand = random.sample(range(n), 2)
        eid, eab = cand[0], cand[1]
        if eid == eab:
            continue
        table = _rand_table(n)
        for j in range(n):
            table[eid][j] = j
            table[j][eid] = j
            table[eab][j] = eab
            table[j][eab] = eab
        if _unique_identity(table, eid) and _unique_absorbing(table, eab):
            return table, eid, eab
    raise RuntimeError("failed to build identity/absorbing table")


def _unique_identity(table, eid):
    n = len(table)
    for e in range(n):
        if e == eid:
            continue
        if all(table[e][j] == j for j in range(n)) and all(table[j][e] == j for j in range(n)):
            return False
    return True


def _unique_absorbing(table, eab):
    n = len(table)
    for a in range(n):
        if a == eab:
            continue
        if all(table[a][j] == a for j in range(n)) and all(table[j][a] == a for j in range(n)):
            return False
    return True


def _leaf(kind, n):
    if kind == "v":
        return ["v"]
    return ["c", random.randrange(n)]


def _build_tree(nleaves):
    if nleaves == 1:
        return ["leaf"]
    l = random.randint(1, nleaves - 1)
    return ["o", _build_tree(l), _build_tree(nleaves - l)]


def _attach(tree, leaves):
    if tree[0] == "leaf":
        return leaves.pop(0) if leaves else None
    _, L, R = tree
    nl = _attach(L, leaves)
    nr = _attach(R, leaves)
    return ["o", nl, nr]


def _eval(expr, table, x):
    k = expr[0]
    if k == "c":
        return expr[1]
    if k == "v":
        return x
    _, L, R = expr
    return table[_eval(L, table, x)][_eval(R, table, x)]


def _render_expr(expr):
    k = expr[0]
    if k == "c":
        return str(expr[1])
    if k == "v":
        return "x"
    _, L, R = expr
    return f"({_render_expr(L)} \u2299 {_render_expr(R)})"


def _render_table(table):
    n = len(table)
    lines = []
    head = "    " + " ".join(str(j) for j in range(n))
    lines.append(head)
    for i in range(n):
        lines.append(f"{i}   " + " ".join(str(v) for v in table[i]))
    return "\n".join(lines)


class CayleyTableEvaluation(Task):
    summary = ("Invented binary operations given as Cayley tables over small carrier sets: "
               "evaluate nested terms, solve one-unknown equations (variable occurring more "
               "than once, unique solution found by exhausting the carrier), and pick out "
               "unique identity or absorbing elements; answers are single elements or "
               "element-pairs.")
    design_choice = ("Generate equations with one unknown variable appearing multiple times; "
                     "require solving via backtracking over all carrier elements, ensuring unique solution.")
    config_cls = CayleyEvalConfig

    def generate_entry(self):
        cfg = self.config
        n = random.randint(cfg.n_min, cfg.n_max)
        carrier = list(range(n))
        mode = random.choices([1, 2, 3], weights=[0.35, 0.45, 0.20])[0]

        if mode == 1:
            table = _rand_table(n)
            nleaves = random.randint(2, cfg.max_leaves)
            leaves = [_leaf("c", n) for _ in range(nleaves)]
            expr = _attach(_build_tree(nleaves), leaves)
            answer = _eval(expr, table, 0)
            metadata = edict(mode=mode, table=table, expr=expr, n=n)
            return Entry(metadata=metadata, answer=str(answer))

        if mode == 2:
            min_occ = 2
            for _ in range(cfg.max_attempts):
                table = _rand_table(n)
                nleaves = random.randint(min_occ + 1, cfg.max_leaves)
                var_occ = random.randint(min_occ, nleaves - 1)
                idxs = random.sample(range(nleaves), var_occ)
                leaves = []
                for i in range(nleaves):
                    leaves.append(_leaf("v", n) if i in idxs else _leaf("c", n))
                expr = _attach(_build_tree(nleaves), leaves)
                s = random.choice(carrier)
                rhs = _eval(expr, table, s)
                sols = [v for v in carrier if _eval(expr, table, v) == rhs]
                if len(sols) == 1:
                    metadata = edict(mode=mode, table=table, expr=expr, rhs=rhs, n=n)
                    return Entry(metadata=metadata, answer=str(sols[0]))
            raise RuntimeError("failed to build unique-solution equation")

        table, eid, eab = _table_with_identity_absorbing(n)
        metadata = edict(mode=mode, table=table, n=n)
        return Entry(metadata=metadata, answer=f"{eid};{eab}")

    def render_prompt(self, metadata):
        table = _render_table(metadata.table)
        head = (
            f"A binary operation \u2299 on the carrier set {list(range(metadata.n))} is defined by "
            f"the table below (row = left operand, column = right operand).\n{table}\n"
        )
        if metadata.mode == 1:
            return head + (
                f"Evaluate the nested term \u2299{_render_expr(metadata.expr)}. "
                "The answer is the single resulting element."
            )
        if metadata.mode == 2:
            return head + (
                f"Consider the equation with the unknown element x in {list(range(metadata.n))}:\n"
                f"{_render_expr(metadata.expr)} = {metadata.rhs}\n"
                "Try x = 0, 1, ..., n-1, traversing every carrier element, and keep the values "
                "that make the equation true. Exactly one such value exists. The answer is that "
                "single element."
            )
        return head + (
            "Identify the (unique) identity element i (i\u2299y = y and y\u2299i = y for every y) "
            "and the (unique) absorbing element a (a\u2299y = a and y\u2299a = a for every y). "
            "Answer as \"i;a\"."
        )

    def score_answer(self, answer, entry):
        norm = lambda s: " ".join(str(s).replace(",", " ").split())
        return float(norm(answer) == norm(entry.answer))


TASK_META = {'parent_source_id': None,
 'idea': 'cayley_table_evaluation (draw 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_parsing_and_agreement_r1/cayley_table_evaluation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2302342651,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
