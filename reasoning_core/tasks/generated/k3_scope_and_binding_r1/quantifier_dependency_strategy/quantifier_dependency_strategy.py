"""Quantifier-dependence games on small domains.

Solve quantifier-dependence games on small domains covering linear,
dependent-choice, branching and slashed-independence prefixes; determine the
winner and output the strategy as per-universal choice functions.
"""

import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


TASK_META = {'parent_source_id': None,
 'idea': 'quantifier_dependency_strategy (draw 1 of 3)',
 'hypothesis': 'P005',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_scope_and_binding_r1/quantifier_dependency_strategy',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 729651269,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class QDependencyConfig(Config):
    """Prefix family configuration."""

    family: str = "linear"
    n_existential: int = 2
    n_universal: int = 2
    domain_size: int = 3

    def apply_difficulty(self, level):
        if level >= 4:
            self.family = "slashed"
        elif level >= 2:
            self.family = "branching"
        elif level >= 1:
            self.family = "dependent"
        else:
            self.family = "linear"

        self.domain_size = 2 if level == 0 else 3
        self.n_existential = 2 + (1 if level >= 3 else 0)
        self.n_universal = 2 + (1 if level >= 5 else 0)


def _all_assignments(dom, arity):
    return list(itertools.product(range(dom), repeat=arity))


def _idx(args, dom):
    i = 0
    for a in args:
        i = i * dom + a
    return i


def _table_at(table, args, dom):
    vals = list(args)
    if not vals:
        return table[0] if len(table) == 1 else table
    return table[_idx(vals, dom)]


def _dep_sets(family, n_univ, n_ex):
    """Per-existential (u_deps, e_deps): which universal / earlier-existential
    variables existential i may read."""
    u_deps, e_deps = [], []
    for i in range(n_ex):
        if family == "linear":
            u_deps.append(list(range(min(i + 1, n_univ))))
            e_deps.append([])
        elif family == "dependent":
            u_deps.append([0] if i > 0 else [])
            e_deps.append(list(range(i)))
        elif family == "branching":
            u_deps.append([i % n_univ])
            e_deps.append([])
        else:  # slashed
            u_deps.append([i] if i < n_univ else [0])
            e_deps.append(list(range(i)))
    return u_deps, e_deps


def _make_existential_win(family, n_univ, n_ex, dom):
    """Construct an instance where the existential player wins. Returns
    (clauses, strategy) where strategy maps each universal assignment to the
    chosen existential values. A var index v>=0 means u_v, v<0 means e_(-v-1)."""
    u_deps, e_deps = _dep_sets(family, n_univ, n_ex)
    g_values = []  # g_i table over (u_deps[i], e_deps[i]) -> existential value
    for i in range(n_ex):
        arity = len(u_deps[i]) + len(e_deps[i])
        g_values.append(tuple(random.randint(0, dom - 1) for _ in range(dom ** arity)))

    def e_at(u, i, evals):
        argvals = tuple(u[j] for j in u_deps[i]) + tuple(evals[j] for j in e_deps[i])
        return _table_at(g_values[i], argvals, dom)

    strategy = {}
    for ua in _all_assignments(dom, n_univ):
        evals = [None] * n_ex
        for i in range(n_ex):
            evals[i] = e_at(ua, i, evals)
        strategy[ua] = tuple(evals)

    clauses = []
    for i in range(n_ex):
        vars_list = list(u_deps[i]) + [-1 * (j + 1) for j in e_deps[i]] + [-1 * (i + 1)]
        size = dom ** len(vars_list)
        table = []
        for combo in _all_assignments(dom, len(vars_list)):
            u_part = tuple(combo[k] for k in range(len(u_deps[i])))
            e_part = tuple(combo[len(u_deps[i]) + k] for k in range(len(e_deps[i])))
            chosen = e_at(dict(zip(u_deps[i], u_part)), i, list(e_part))
            e_i_val = combo[-1]
            table.append(1 if e_i_val == chosen else 0)
        clauses.append((tuple(vars_list), tuple(table)))
    return clauses, strategy


def _make_universal_win(family, n_univ, n_ex, dom):
    """Construct an instance where the universal player wins by adding a
    blocking universal-only clause that is false for at least one universal
    assignment. Returns (clauses, None)."""
    clauses, _ = _make_existential_win(family, n_univ, n_ex, dom)
    k = random.randint(1, min(2, n_univ))
    uv = sorted(random.sample(range(n_univ), k))
    size = dom ** k
    table = [random.randint(0, 1) for _ in range(size)]
    if all(v == 1 for v in table):
        table[random.randrange(size)] = 0
    vars_list = list(uv)
    clauses.append((tuple(vars_list), tuple(table)))
    return clauses, None


def _answer_str(strategy, dom, n_univ):
    rows = []
    for ua in sorted(strategy):
        e = strategy[ua]
        rows.append(";".join(str(x) for x in ua) + "->" +
                    ";".join(str(x) for x in e))
    return " | ".join(rows)


class QuantifierDependencyStrategy(Task):
    summary = ("Solve quantifier-dependence games on small domains covering linear, "
               "dependent-choice, branching and slashed-independence prefixes; determine "
               "the winner and output the strategy as per-universal choice functions.")
    config_cls = QDependencyConfig
    design_choice = ("Strategy output as a table mapping each universal variable "
                     "assignment to the existential's chosen value, with winner "
                     "determined by evaluating the formula over that table.")

    def generate_entry(self):
        family = self.config.family
        n_univ = self.config.n_universal
        n_ex = self.config.n_existential
        dom = self.config.domain_size

        universal_win = random.random() < 0.20
        if universal_win:
            clauses, strategy = _make_universal_win(family, n_univ, n_ex, dom)
            exists_win = False
        else:
            clauses, strategy = _make_existential_win(family, n_univ, n_ex, dom)
            exists_win = True

        metadata = {
            "family": family,
            "n_universal": n_univ,
            "n_existential": n_ex,
            "domain_size": dom,
            "clauses": clauses,
            "winning": exists_win,
        }

        if exists_win:
            answer = _answer_str(strategy, dom, n_univ)
        else:
            answer = "UNIVERSAL"

        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        family = metadata["family"]
        n_univ = metadata["n_universal"]
        n_ex = metadata["n_existential"]
        dom = metadata["domain_size"]
        clauses = metadata["clauses"]

        prefix_label = {
            "linear": (
                f"after the universals u0..u{max(n_univ-1,0)} are fixed, the "
                f"existentials e0..e{n_ex-1} are chosen in linear order, each e[j] "
                f"able to see the universals u0..u[j]"),
            "dependent": (
                f"dependent choice: e0 is chosen freely, and each later existential "
                f"may depend on all earlier existentials and on u0"),
            "branching": (
                f"branching independence: each existential group depends on one "
                f"dedicated universal and the groups commit simultaneously"),
            "slashed": (
                f"slashed independence: each existential e[j] depends on u[j] and on "
                f"all earlier existentials, independent of every other universal"),
        }[family]

        def varname(v):
            return ("u%d" % v) if v >= 0 else ("e%d" % (-v - 1))

        clause_lines = []
        for ci, (vars_list, table) in enumerate(clauses):
            vdesc = ",".join(varname(v) for v in vars_list)
            cells = ", ".join(str(int(v)) for v in table)
            clause_lines.append(f"C{ci}({vdesc}) = [{cells}]")
        clauses_text = " | ".join(clause_lines)

        prompt = (
            f"Domain D = {{{', '.join(str(x) for x in range(dom))}}}. "
            f"The quantifier prefix is: for every universal assignment there exists "
            f"an existential assignment; {prefix_label}.\n"
            f"Formula clauses (each is a boolean truth table over its listed "
            f"arguments, values in increasing order, least-significant last; the "
            f"conjunction of all clauses must hold):\n"
            f"{clauses_text}\n"
            f"The universal player wins if some universal assignment makes the "
            f"conjunction false for every existential choice; the existential player "
            f"wins otherwise, choosing one existential value per universal assignment.\n"
            f"Name the winner. If the existential player wins, give its strategy as a "
            f"table mapping each universal assignment to the chosen existential values, "
            f"rows sorted lexicographically and joined by ' | ', each row of the form "
            f"'u0;u1->e0;e1'. If the universal player wins, output the single word "
            f"UNIVERSAL."
        )
        return prompt

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        n_univ = metadata["n_universal"]
        n_ex = metadata["n_existential"]
        dom = metadata["domain_size"]

        if not metadata["winning"]:
            return 1.0 if answer.strip().upper() == "UNIVERSAL" else 0.0

        strat = _parse_strategy(answer, dom, n_univ, n_ex)
        if strat is None:
            return 0.0
        for ua, ea in strat.items():
            for vars_list, table in metadata["clauses"]:
                args = tuple(ua[v] if v >= 0 else ea[-v - 1] for v in vars_list)
                if _table_at(table, args, dom) == 0:
                    return 0.0
        return 1.0


def _parse_strategy(answer, dom, n_univ, n_ex):
    try:
        strat = {}
        for chunk in answer.split("|"):
            chunk = chunk.strip()
            if not chunk:
                continue
            if "->" not in chunk:
                return None
            lhs, rhs = chunk.split("->")
            ua = tuple(int(x) for x in lhs.split(";") if x != "")
            e = tuple(int(x) for x in rhs.split(";") if x != "")
            if len(ua) != n_univ or len(e) != n_ex:
                return None
            if any(x < 0 or x >= dom for x in ua + e):
                return None
            strat[ua] = e
        if len(strat) != dom ** n_univ:
            return None
        return strat
    except ValueError:
        return None
