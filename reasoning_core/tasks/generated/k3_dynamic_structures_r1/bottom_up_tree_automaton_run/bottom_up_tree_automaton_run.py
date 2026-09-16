import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


TASK_META = {'parent_source_id': None,
 'idea': 'bottom_up_tree_automaton_run (draw 3 of 3, unguided baseline)',
 'hypothesis': 'P004',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/bottom_up_tree_automaton_run',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1339177894,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _gen_tree(symbols, depth, max_nodes):
    def build(cur_depth, budget):
        leaf = (random.choice(symbols), ())
        if cur_depth <= 0 or budget <= 1:
            return leaf
        arity = random.randint(0, 2)
        if arity == 0:
            return leaf
        arity = min(arity, budget - 1)
        child_budget = max(1, (budget - 1) // arity)
        children = tuple(build(cur_depth - 1, child_budget) for _ in range(arity))
        return (random.choice(symbols), children)
    return build(depth, max_nodes)


def _run_automaton(leaf_map, table, tree):
    def rec(node):
        label, children = node
        if not children:
            return frozenset(leaf_map[label])
        child_state_sets = [rec(c) for c in children]
        acc = set()
        for combo in itertools.product(*child_state_sets):
            combo = tuple(sorted(combo))
            res = table.get((label, combo), ())
            acc.update(res)
        return frozenset(acc)
    return rec(tree)


def _tree_str(node, symbols):
    label, children = node
    if not children:
        return label
    inner = " ".join(_tree_str(c, symbols) for c in children)
    return f"({label} {inner})"


def _answer_for(root_states, accepted):
    states = " ".join(f"s{x}" for x in sorted(root_states)) if root_states else ""
    return f"{{{states}}}|{accepted}"


def _parse_answer(answer, num_states):
    a = str(answer).strip()
    if a == _answer_for([], "no"):
        return set()
    if not (a.endswith("|yes") or a.endswith("|no")):
        return None
    body, _, acc = a.rpartition("|")
    if acc not in ("yes", "no"):
        return None
    if not (body.startswith("{") and body.endswith("}")):
        return None
    inner = body[1:-1].strip()
    if not inner:
        states = set()
    else:
        parts = [p for p in inner.split() if p]
        try:
            states = {int(p[1:]) for p in parts}
        except Exception:
            return None
    if any(s < 0 or s >= num_states for s in states):
        return None
    return states


@dataclass
class AutomatonConfig(Config):
    num_leaves: int = 3
    num_states: int = 2
    tree_depth: int = 1

    def apply_difficulty(self, level):
        self.num_leaves = stochastic_rounding(self.num_leaves + (level // 2))
        self.num_states = stochastic_rounding(self.num_states + (level // 3))
        self.tree_depth = stochastic_rounding(self.tree_depth + (level // 2) + level)


class BottomUpTreeAutomatonRun(Task):
    summary = ("Run a nondeterministic bottom-up tree automaton over labeled ordered "
               "trees: leaf symbols map to state sets, parents combine child-state tuples "
               "via a transition table; answer is the root state set and acceptance.")

    config_cls = AutomatonConfig

    def generate_entry(self):
        cfg = self.config
        num_states = min(3, max(2, cfg.num_states))
        num_leaves = max(2, min(5, cfg.num_leaves))
        states = list(range(num_states))
        symbols = [f"s{i}" for i in range(num_leaves)]
        root_sym = random.choice(symbols)
        inner_symbols = [s for s in symbols if s != root_sym]

        leaf_map = {}
        for sym in symbols:
            leaf_map[sym] = sorted(random.sample(states, random.randint(1, num_states)))

        # Inner symbols: total unary + binary transition rules with non-empty results,
        # so any subtree built from them stays non-empty (never dead-ends).
        table = {}
        for sym in inner_symbols:
            for s in states:
                table[(sym, (s,))] = sorted(
                    random.sample(states, random.randint(1, num_states)))
            for a in range(num_states):
                for b in range(num_states):
                    table[(sym, tuple(sorted((a, b))))] = sorted(
                        random.sample(states, random.randint(1, num_states)))

        depth = max(1, min(cfg.tree_depth, 4))
        budget = min(6 + 3 * depth, 28)
        root_arity = random.randint(1, 2)
        root_children = tuple(
            _gen_tree(inner_symbols, depth - 1, budget // root_arity)
            for _ in range(root_arity))
        tree = (root_sym, root_children)

        # Compute each root-child state set (root itself has no rule yet).
        child_sets = [_run_automaton(leaf_map, table, c) for c in root_children]

        target = "no" if random.random() < 0.32 else "yes"
        if target == "yes":
            for combo in itertools.product(*child_sets):
                table[(root_sym, tuple(sorted(combo)))] = sorted(
                    random.sample(states, random.randint(1, num_states)))
            root = _run_automaton(leaf_map, table, tree)
        else:
            root = frozenset()

        root_states = sorted(root)
        accepted = "yes" if root_states else "no"
        assert (accepted == target)
        assert 0 <= len(root_states) <= num_states

        node_names = {sym: sym for sym in symbols}
        tstr = _tree_str(tree, node_names)
        answer = _answer_for(root_states, accepted)

        table_rows = [
            {"symbol": k[0], "child_states": list(k[1]), "result": v}
            for k, v in sorted(table.items(), key=lambda kv: (kv[0][0], tuple(kv[0][1])))
        ]

        return Entry(
            metadata={
                "tree": tstr,
                "leaf_map": {k: list(v) for k, v in leaf_map.items()},
                "table": table_rows,
                "root_states": root_states,
                "accepted": accepted,
                "num_states": num_states,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        lines = [
            "A nondeterministic bottom-up tree automaton is defined over an ordered tree.",
            "",
            "Tree (symbols are the node labels; children of an internal node follow it in "
            "parentheses, leaves have none):",
            metadata["tree"],
            "",
            "Leaf symbols map to sets of states:",
        ]
        for k in sorted(metadata["leaf_map"]):
            lines.append(f"  {k} -> {{{' '.join(f's{x}' for x in metadata['leaf_map'][k])}}}")
        lines.append("")
        lines.append("Transition rules: parent symbol with a child-state tuple gives the result "
                     "state set")
        for row in metadata["table"]:
            cs = row["child_states"]
            lines.append(f"  {row['symbol']} with children {{{' '.join(f's{x}' for x in cs)}}} -> "
                         "{" + " ".join(f"s{r}" for r in row["result"]) + "}")
        lines.append("")
        lines.append("Compute the set of states reachable at the root, combining child-state sets "
                     "bottom-up: a child reaches whatever its sub-automaton computes, and a parent "
                     "with children reaching states S1..Sk reaches every union over a compatible "
                     "rule. It accepts iff its root state set is non-empty.")
        lines.append("")
        lines.append("Answer as one line: the root state set in braces (states written as s<n>, "
                     "space-separated, in increasing order; {} if empty) followed by |yes or |no. "
                     "Example: {s0 s2}|yes")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        metadata = entry.metadata
        num_states = metadata["num_states"]
        parsed = _parse_answer(answer, num_states)
        if parsed is None:
            return 0.0
        gold_states = set(metadata["root_states"])
        gold_acc = metadata["accepted"]
        states_ok = parsed == gold_states
        acc_ok = (gold_acc == "yes") == bool(parsed)
        if states_ok and acc_ok:
            return 1.0
        return 0.0
