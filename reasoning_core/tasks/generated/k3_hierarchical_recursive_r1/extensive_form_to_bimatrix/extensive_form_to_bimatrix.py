import random
from dataclasses import dataclass
from fractions import Fraction

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'extensive_form_to_bimatrix (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/extensive_form_to_bimatrix',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 368817805,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


_INTRO = (
    "In an extensive-form game, a pure strategy for a player chooses one action at "
    "every one of that player's decision nodes. A strategy profile fixes a terminal "
    "node; a chance node contributes its probability-weighted (expected) payoff. The "
    "induced normal-form (bimatrix) payoff table lists, for every pair of pure "
    "strategies (one per player), the (payoff to Player 1, payoff to Player 2) "
    "expected payoff pair."
)


def _fmt_frac(fr):
    n, d = fr.numerator, fr.denominator
    if d == 1:
        return str(n)
    return f"{n}/{d}"


def _term_expected(t):
    if t[0] == "pay":
        return (Fraction(t[1][0]), Fraction(t[1][1]))
    _, outcomes, den = t
    e1 = Fraction(0)
    e2 = Fraction(0)
    for w, p in outcomes:
        e1 += Fraction(w, den) * p[0]
        e2 += Fraction(w, den) * p[1]
    return (e1, e2)


def _render_payoff(pair):
    return f"({_fmt_frac(pair[0])},{_fmt_frac(pair[1])})"


def _build_instance(cfg):
    max_b = cfg.branch_max
    valid = [(2, 2)]
    if max_b >= 3:
        valid += [(3, 2), (2, 3)]
    if max_b >= 4:
        valid += [(2, 4)]
    b1, b2 = random.choice(valid)
    pmax = cfg.payoff_max
    p2_nodes = []
    for _ in range(b1):
        node_actions = []
        for _ in range(b2):
            if random.random() < cfg.chance_prob:
                den = random.choice([2, 3])
                w1 = random.randint(1, den - 1)
                w2 = den - w1
                pa = (random.randint(-pmax, pmax), random.randint(-pmax, pmax))
                pb = (random.randint(-pmax, pmax), random.randint(-pmax, pmax))
                node_actions.append(("lot", [(w1, pa), (w2, pb)], den))
            else:
                p = (random.randint(-pmax, pmax), random.randint(-pmax, pmax))
                node_actions.append(("pay", p))
        p2_nodes.append(node_actions)
    return b1, b2, p2_nodes


def _render_tree(b1, b2, p2_nodes):
    lines = [f"- Player 1 (root) has {b1} branches."]
    for i in range(b1):
        lines.append(f"- Branch {i + 1}: Player 2 node #{i + 1} has {b2} actions:")
        for k in range(b2):
            t = p2_nodes[i][k]
            if t[0] == "pay":
                desc = f"payoff ({t[1][0]},{t[1][1]})"
            else:
                _, outs, den = t
                lott = ", ".join(
                    f"{_fmt_frac(Fraction(w, den))}: ({p[0]},{p[1]})" for w, p in outs
                )
                desc = f"chance {{ {lott} }}"
            lines.append(f"    - action {k + 1} -> terminal: {desc}")
    return "\n".join(lines)


def _compute_matrix(b1, b2, p2_nodes):
    cols = b2 ** b1
    matrix = []
    for i in range(b1):
        row = []
        for j in range(cols):
            tup = [(j // (b2 ** (b1 - 1 - k))) % b2 for k in range(b1)]
            row.append(_term_expected(p2_nodes[i][tup[i]]))
        matrix.append(row)
    return matrix


def _format_answer(matrix):
    rows = [" | ".join(_render_payoff(p) for p in row) for row in matrix]
    return " ; ".join(rows)


@dataclass
class ExtensiveBimatrixConfig(Config):
    branch_max: int = 2
    payoff_max: int = 4
    chance_prob: float = 0.35

    def apply_difficulty(self, level):
        self.branch_max = 2 + level
        self.payoff_max = 4 + 3 * level
        self.chance_prob = min(0.7, 0.35 + 0.07 * level)


class ExtensiveFormToBimatrix(Task):
    summary = ("Enumerate both players' pure strategies in a small perfect-information "
               "extensive-form game tree with varying branch counts, optional terminal "
               "chance nodes resolved by exact expectation producing integer or rational "
               "payoffs, and emit the induced normal-form payoff bimatrix in canonical "
               "strategy order.")
    config_cls = ExtensiveBimatrixConfig
    task_version = 3

    def generate_entry(self):
        cfg = self.config
        b1, b2, p2_nodes = _build_instance(cfg)
        matrix = _compute_matrix(b1, b2, p2_nodes)
        for row in matrix:
            for (e1, e2) in row:
                assert e1.denominator >= 1 and e2.denominator >= 1
                assert isinstance(e1, Fraction) and isinstance(e2, Fraction)
        check = _compute_matrix(b1, b2, p2_nodes)
        assert check == matrix
        answer = _format_answer(matrix)

        tree_text = _render_tree(b1, b2, p2_nodes)
        matrix_json = [
            [_render_payoff(pair) for pair in row] for row in matrix
        ]
        return Entry(metadata={
            "b1": b1,
            "b2": b2,
            "tree": tree_text,
            "matrix": matrix_json,
            "answer": answer,
            "chance_prob": cfg.chance_prob,
        }, answer=answer)

    def render_prompt(self, metadata):
        order = (
            "Strategy order: rows are Player 1's pure strategies in order of the root "
            "branch chosen (branch 1, branch 2, ...). Columns are Player 2's pure "
            "strategies, each written as the tuple of actions chosen at Player 2's "
            f"decision nodes #{1}..#{metadata['b1']} from top to bottom, ordered "
            "lexicographically by these tuples."
        )
        fmt = (
            "Give the induced normal-form payoff bimatrix. Format: list the rows in "
            'order separated by " ; ", and within each row list the column payoff pairs '
            'left to right separated by " | ". Write each entry as '
            "(payoff_to_P1,payoff_to_P2) with fractions in lowest terms (for example "
            "5/2) and integers as plain numbers."
        )
        return (
            f"{_INTRO}\n\nConsider this perfect-information extensive-form game where "
            "Player 1 chooses first at the root, then Player 2.\n\nGame tree:\n"
            f"{metadata['tree']}\n\n{order}\n\n{fmt}"
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == str(entry["answer"]).strip() else 0.0
