"""Top-down tree transducer execution.

A deterministic top-down tree transducer consumes the nodes of a ranked input tree
left-to-right from the root. Each (state, label) pair chooses a rule: emit a leaf
output word, emit a subtree template that reassigns states for (a possibly reordered,
dropped subset of) the node's children, or have no applicable rule. Running it yields
a serialized output tree, or fails at the first node where no rule applies.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

RULE_WORDS = [
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
    "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "rho",
]

LABELS = [
    "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l",
]

STATES = [
    "p", "q", "r", "s", "t", "u", "v", "w",
]


def _child_paths(path):
    return [path + "-" + str(i) for i in range(12)]


def _make_tree(level):
    """Build a random ranked input tree.

    Returns (label_of, children_of, ordered) keyed by path ('' == root), with
    ordered holding pre-order (root first).
    """
    arities = [0, 0, 1, 1, 2, 2, 2, 3]
    max_depth = 2 + level
    label_of = {"": random.choice(LABELS)}
    children_of = {"": []}
    ordered = [""]
    i = 0
    while i < len(ordered):
        path = ordered[i]
        i += 1
        depth = 0 if path == "" else path.count("-")
        if depth >= max_depth:
            continue
        arity = random.choice(arities)
        if arity == 0:
            continue
        kids = []
        ci = 0
        while len(kids) < arity:
            kid = f"{path}-{ci}" if path != "" else str(ci)
            ci += 1
            kids.append(kid)
        children_of[path] = kids
        for kid in kids:
            label_of[kid] = random.choice(LABELS)
            ordered.append(kid)
    return label_of, children_of, ordered


def _make_rule(state_set, max_arity):
    """Build one rule dict for a (state, label) pair. max_arity bounds children."""
    if random.random() < 0.10:
        return {"kind": "none"}
    if random.random() < 0.35:
        return {"kind": "leaf", "word": random.choice(RULE_WORDS)}
    if max_arity == 0:
        return {"kind": "leaf", "word": random.choice(RULE_WORDS)}
    nused = random.randint(1, max_arity)
    order = random.sample(range(max_arity), nused)
    states = [random.choice(state_set) for _ in range(nused)]
    return {"kind": "node", "word": random.choice(RULE_WORDS),
            "states": states, "order": order}


def _run(label_of, children_of, rules, start_state):
    """Execute the transducer from the root in state start_state.

    Returns (status, result): ('ok', serialized_output) or ('stuck', path).
    """
    words = []
    stuck = None

    def walk(state, path):
        nonlocal stuck
        if stuck is not None:
            return
        rule = rules.get((state, label_of[path]))
        if rule is None or rule["kind"] == "none":
            stuck = path
            return
        if rule["kind"] == "leaf":
            words.append(rule["word"])
            return
        words.append(rule["word"])
        words.append("(")
        kids = children_of.get(path, [])
        first = True
        for oi, st in zip(rule["order"], rule["states"]):
            if oi >= len(kids):
                continue
            if not first:
                words.append(",")
            first = False
            walk(st, kids[oi])
            if stuck is not None:
                return
        words.append(")")

    walk(start_state, "")
    if stuck is not None:
        return ("stuck", stuck)
    return ("ok", "".join(words))


def _fmt_rule(rule):
    if rule["kind"] == "none":
        return "none"
    if rule["kind"] == "leaf":
        return f"leaf {rule['word']}"
    parts = [f"child {oi} in {st}" for oi, st in zip(rule["order"], rule["states"])]
    if not parts:
        return f"node {rule['word']} with no children"
    return f"node {rule['word']} with children: " + ", ".join(parts) + " (in that order)"


def _preorder(children_of):
    ordered = [""]
    i = 0
    while i < len(ordered):
        path = ordered[i]
        i += 1
        for kid in children_of.get(path, []):
            ordered.append(kid)
    return ordered


@dataclass
class TreeConfig(Config):
    level: int = 0

    def apply_difficulty(self, level):
        self.level = level


class TreeTransducerRun(Task):
    summary = (
        "Run top-down tree transducers: states consume input nodes and emit output "
        "templates that recurse into children under reassigned states; answer the "
        "serialized output tree or the input path where no rule applies."
    )
    design_choice = (
        "Output format: parenthesized prefix notation with labels as lowercase words, "
        "and failure reported as the path from root (e.g., '0-1-2') to the first stuck node."
    )
    config_cls = TreeConfig

    def generate_entry(self):
        level = self.config.level
        min_nodes = 5 + level
        max_nodes = 9 + 2 * level
        state_scope = STATES[: min(4 + level, 6)]
        label_scope = LABELS[: min(4 + level, 7)]

        for _ in range(600):
            label_of, children_of, ordered = _make_tree(level)
            if not (min_nodes <= len(ordered) <= max_nodes):
                continue
            max_arity = max((len(children_of.get(p, [])) for p in ordered), default=0)
            rules = {}
            for st in state_scope:
                for lb in label_scope:
                    rules[(st, lb)] = _make_rule(state_scope, max_arity)
            start = random.choice(state_scope)
            status, result = _run(label_of, children_of, rules, start)
            # Domain check: an ok answer must be a nonempty serialized tree, a stuck
            # path must be a nonempty dash-separated integer string (the root itself
            # is never the first stuck node because it always has a rule here).
            if status == "ok":
                if result == "":
                    continue
                answer = result
            else:
                if result == "" or not all(
                    p.isdigit() for p in result.split("-")
                ):
                    continue
                answer = result
            metadata = {
                "label_of": label_of,
                "children_of": children_of,
                "rules": {f"{s}/{l}": rules[(s, l)]
                          for s in state_scope for l in label_scope},
                "start_state": start,
                "outcome": status,
                "max_arity": max_arity,
            }
            return Entry(metadata=metadata, answer=answer)
        raise RuntimeError("could not generate a valid instance in bounded attempts")

    def render_prompt(self, metadata):
        label_of = metadata["label_of"]
        children_of = metadata["children_of"]
        rules = metadata["rules"]
        lines = [
            "A top-down (root-to-leaves) tree transducer runs over an input tree. Each "
            "node has a label and an ordered list of children indexed 0, 1, 2, ... The "
            "transducer assigns a state to each visited node and applies the matching "
            "(state, label) rule.",
            "  - 'leaf WORD': emit the leaf word WORD and stop at this node;",
            "  - 'node WORD with children: child i in STATE, ...' : emit 'WORD ( ... )' "
            "where each listed child (by index) is visited under its STATE, in the "
            "listed order (a child may be dropped or reordered; only listed children "
            "are visited);",
            "  - 'none': no rule applies, the run is stuck (fails) at this node.",
            "Visited children are emitted in pre-order from the root.",
            "Input tree ('*' is the root; each non-leaf line shows label and children "
            "indices):",
        ]
        for path in _preorder(children_of):
            kids = children_of.get(path, [])
            disp = "*" if path == "" else path
            if kids:
                lines.append(f"  {disp}: label {label_of[path]} children {kids}")
            else:
                lines.append(f"  {disp}: label {label_of[path]} (leaf)")
        lines.append("Rules (per 'state/label'):")
        for key, rule in rules.items():
            lines.append(f"  {key}: {_fmt_rule(rule)}")
        lines.append(f"Start state: {metadata['start_state']}")
        lines.append(
            "Run the transducer. If it completes, answer the serialized output tree in "
            "parenthesized prefix notation (a leaf is its word; a node with template "
            "WORD and visited children C1, C2 is 'WORD ( C1 , C2 )') on one line."
        )
        lines.append(
            "If the run gets stuck, answer the path from the root to the FIRST stuck "
            "node in pre-order as dash-separated child indices (e.g. '0-1-2'). The root "
            "itself is never the first stuck node."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        gold = entry.answer
        if not isinstance(answer, str):
            return 0.0
        return 1.0 if answer.strip() == gold else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'tree_transducer_run (variant 2 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_paraphrase_equivalence_r1/tree_transducer_run',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.30',
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
