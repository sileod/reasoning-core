import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'tag_adjunction_derivation (draw 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_formal_semantics_r1/tag_adjunction_derivation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 682015719,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

TERMINALS = ["a", "b", "c", "d", "e"]
NONTERMINALS = ["S", "NP", "VP"]

NP_SLOT = ("NP", ("#",))
VP_SLOT = ("VP", ("#",))


def _random_initial():
    """A randomly shaped initial tree; roots S, NP or VP, sometimes carrying a
    nested slot of its own category to enable recursive substitution growth."""
    t = random.choice(TERMINALS)
    i = random.randrange(7)
    if i == 0:
        return ("S", (NP_SLOT, VP_SLOT))
    if i == 1:
        return ("S", (t, VP_SLOT))
    if i == 2:
        return ("S", (NP_SLOT, t))
    if i == 3:
        return ("NP", (t,))
    if i == 4:
        return ("NP", (t, NP_SLOT))
    if i == 5:
        return ("VP", (t,))
    return ("VP", (t, VP_SLOT))


def flat_yield(tree):
    """Yield of a tree (list of terminals), dropping '#' frontier markers."""
    if isinstance(tree, str):
        return [] if tree == "#" else [tree]
    _, children = tree
    out = []
    for ch in children:
        out.extend(flat_yield(ch))
    return out


def frontier_paths(tree, parent_label=None, path=()):
    """Paths to frontier ('#') leaves, each tagged with its parent label.

    Returns list of (path, parent_label).
    """
    if isinstance(tree, str):
        return []
    label, children = tree
    out = []
    for i, ch in enumerate(children):
        if isinstance(ch, str):
            if ch == "#":
                out.append((path + (i,), label))
        else:
            out.extend(frontier_paths(ch, label, path + (i,)))
    return out


def is_leaf(tree):
    return isinstance(tree, str) and tree != "#"


def find_internal_labeled(tree, target, path=()):
    """Path to an internal node labeled target, or None.

    Internal means a real (non-terminal-children) internal node, not a leaf and
    not a frontier slot.
    """
    if isinstance(tree, str):
        return None
    label, children = tree
    if children == ("#",):
        return None
    if all(isinstance(c, str) for c in children):
        return None
    if label == target:
        return path
    for i, ch in enumerate(children):
        if isinstance(ch, str):
            continue
        p = find_internal_labeled(ch, target, path + (i,))
        if p is not None:
            return p
    return None


def substitute_at(tree, path, init_tree):
    """Replace the subtree at path by init_tree."""
    if isinstance(tree, str):
        return init_tree
    label, children = tree
    if not path:
        return init_tree
    i = path[0]
    out = list(children)
    out[i] = substitute_at(out[i], path[1:], init_tree)
    return (label, tuple(out))


def subtree_at(tree, path):
    if not path:
        return tree
    return subtree_at(tree[1][path[0]], path[1:])


def _fill_foot(aux, sub):
    """Return aux with its '#' foot leaf replaced by sub."""
    if isinstance(aux, str):
        return sub if aux == "#" else aux
    label, children = aux
    return (label, tuple(_fill_foot(ch, sub) for ch in children))


def adjoin_at(tree, path, aux):
    """True adjunction: replace the node at path with aux whose foot carries the
    original subtree, preserving the category at that node."""
    sub = subtree_at(tree, path)
    filled = _fill_foot(aux, sub)
    return substitute_at(tree, path, filled)


def to_meta(tree):
    if isinstance(tree, str):
        return tree
    return (tree[0], tuple(to_meta(c) for c in tree[1]))


def _random_aux(label):
    return (label, (random.choice(TERMINALS), "#", random.choice(TERMINALS)))


def _describe_op(op):
    kind, payload = op
    root = payload[0]
    if kind == "sub":
        return "substitute " + root
    return "adjoin " + root


@dataclass
class TagConfig(Config):
    min_steps: int = 3
    max_steps: int = 4
    aux_share: float = 0.0

    def apply_difficulty(self, level):
        self.min_steps = 2 + level
        self.max_steps = 3 + 2 * level
        self.aux_share = min(0.3 + 0.12 * level, 0.85)


class TagAdjunctionDerivation(Task):
    summary = ("Grow tree-adjoining-grammar derivations by substituting initial "
               "trees at frontier nodes and adjoining auxiliary trees at "
               "category-matching nodes; answers are the derived yield, the next "
               "legal operation, or a validity verdict.")
    design_choice = ("Answer forms alternate: derived yield as a space-separated terminal "
                     "string, next legal operation as a canonical action string, or "
                     "validity verdict as yes/no, balanced across instances.")

    config_cls = TagConfig

    def generate_entry(self):
        config = self.config
        steps = random.randint(config.min_steps, config.max_steps)
        mode = random.choice(["yield", "action", "validity"])

        if mode == "yield" or steps == 1:
            for _ in range(200):
                ops = self._legal_ops(steps)
                tree, applied = self.apply_ops(ops)
                y = " ".join(flat_yield(tree))
                if y.strip():
                    break
            else:
                raise RuntimeError("could not produce a non-empty yield")
            return Entry(
                metadata={
                    "mode": "yield",
                    "ops": [_describe_op(o) for o in ops],
                    "tree": to_meta(tree),
                },
                answer=y,
            )
        if mode == "action":
            return self._entry_action(steps)
        return self._entry_validity(steps)

    def _legal_ops(self, steps):
        ops = [self._random_op() for _ in range(steps)]
        ops[0] = ("sub", _random_initial())
        return ops

    def _random_op(self):
        if random.random() < self.config.aux_share:
            return ("adj", _random_aux(random.choice(NONTERMINALS)))
        return ("sub", _random_initial())

    def _entry_action(self, steps):
        stop = random.randint(1, steps - 1)
        prefix = self._legal_ops(stop)
        illegal = self._make_illegal_single(prefix)
        ops = prefix + [illegal]
        return Entry(
            metadata={
                "mode": "action",
                "ops": [_describe_op(o) for o in ops],
                "next_idx": stop,
                "next_action": _describe_op(illegal),
            },
            answer=_describe_op(illegal),
        )

    def _make_illegal_single(self, prefix):
        tree, applied = self.apply_ops(prefix)
        for _ in range(200):
            optype = random.choice(["sub", "adj"])
            if optype == "adj":
                nt = random.choice(NONTERMINALS)
                if find_internal_labeled(tree, nt) is None:
                    return ("adj", _random_aux(nt))
            else:
                init_tree = _random_initial()
                if not frontier_paths(tree) or not any(
                    lbl == init_tree[0] for _p, lbl in frontier_paths(tree)
                ):
                    return ("sub", init_tree)
        raise RuntimeError("could not create illegal op")

    def apply_ops(self, ops):
        """Apply ops in order, returning (tree, applied_indices)."""
        first = ops[0]
        if first[0] != "sub":
            return None, [0]
        tree = first[1]
        applied = [0]
        for idx in range(1, len(ops)):
            kind, payload = ops[idx]
            if kind == "sub":
                fronts = frontier_paths(tree)
                match = [(p, lbl) for p, lbl in fronts if lbl == payload[0]]
                if not match:
                    return tree, applied
                path, _ = random.choice(match)
                tree = substitute_at(tree, path, payload)
            else:
                path = find_internal_labeled(tree, payload[0])
                if path is None:
                    return tree, applied
                tree = adjoin_at(tree, path, payload)
            applied.append(idx)
        return tree, applied

    def _entry_validity(self, steps):
        ops = self._legal_ops(steps)
        if random.random() < 0.5:
            return Entry(
                metadata={
                    "mode": "validity",
                    "ops": [_describe_op(o) for o in ops],
                    "verdict": "yes",
                },
                answer="yes",
            )
        render_ops = self._make_illegal(ops)
        return Entry(
            metadata={
                "mode": "validity",
                "ops": [_describe_op(o) for o in render_ops],
                "verdict": "no",
            },
            answer="no",
        )

    def _make_illegal(self, ops):
        for _ in range(200):
            cand = list(ops)
            idx = random.randrange(1, len(cand))
            tree_prefix, _ = self.apply_ops(cand[:idx])
            option = random.choice(["sub", "adj"])
            if option == "adj":
                nt = random.choice(NONTERMINALS)
                if find_internal_labeled(tree_prefix, nt) is not None:
                    continue
                cand[idx] = ("adj", _random_aux(nt))
            else:
                init_tree = _random_initial()
                good = any(
                    lbl == init_tree[0] for _p, lbl in frontier_paths(tree_prefix)
                )
                if good:
                    continue
                cand[idx] = ("sub", init_tree)
            tree, applied = self.apply_ops(cand)
            if tree is not None and len(applied) < len(cand):
                return cand
        raise RuntimeError("could not make illegal")

    def render_prompt(self, metadata):
        m = metadata
        if m["mode"] == "yield":
            return (
                "In a tree-adjoining grammar, trees grow by substitution and "
                "adjunction. The first operation below supplies the initial tree; "
                "each later operation is applied in turn. A 'substitute X' operation "
                "replaces a frontier node whose parent category is X with an initial "
                "tree rooted at X. An 'adjoin Y' operation replaces an internal node "
                "labeled Y with an auxiliary tree rooted at Y, which has the same "
                "root and a single foot leaf and therefore preserves the category. "
                "An operation that cannot be applied is skipped.\n"
                "Operations: " + "; ".join(m["ops"]) + ".\n"
                "Give the final derived yield (every leaf, left to right) as a "
                "space-separated terminal string, e.g. 'a b c'."
            )
        if m["mode"] == "action":
            return (
                "In a tree-adjoining grammar, trees grow by substitution and "
                "adjunction. The first operation below supplies the initial tree; "
                "the remaining operations are intended for later, in order. A "
                "'substitute X' replaces a frontier node whose parent category is X "
                "with an initial tree rooted at X. An 'adjoin Y' replaces an internal "
                "node labeled Y with an auxiliary tree rooted at Y. Apply the "
                "operations in order, skipping any that cannot be applied.\n"
                "Operations: " + "; ".join(m["ops"]) + ".\n"
                "After the longest legal prefix of these operations, which is the "
                "next operation to attempt? Give its action string exactly as written "
                "in the list, e.g. 'adjoin VP'."
            )
        return (
            "In a tree-adjoining grammar, trees grow by substitution and adjunction. "
            "The first operation supplies the initial tree; the rest are applied in "
            "order. A 'substitute X' replaces a frontier node whose parent is X with "
            "an initial tree rooted at X. An 'adjoin Y' replaces an internal node "
            "labeled Y with an auxiliary tree rooted at Y. An operation that cannot "
            "be applied is skipped.\n"
            "Operations: " + "; ".join(m["ops"]) + ".\n"
            "Can every operation be applied in its given order? Answer yes or no."
        )

    def score_answer(self, answer, entry):
        m = entry.metadata
        if not isinstance(answer, str):
            return 0.0
        if m["mode"] == "validity":
            a = answer.strip().lower()
            return 1.0 if a == entry.answer else 0.0
        return 1.0 if answer.strip() == entry.answer else 0.0

    def score_scalar(self, answer, entry):
        return self.score_answer(answer, entry)
