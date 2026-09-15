"""Ershov register numbering on full binary expression trees.

The summary covers: for a full binary tree (every internal node has two
children) with distinct leaves, we compute the Ershov number of each subtree
bottom-up: a leaf has number 1, and an internal node with children (l, r) has
number max(l, r) if l == r else max(l, r) + 1. The minimal number of registers
needed to evaluate such an expression tree is the Ershov number of the root.

For the optimal evaluation order, at every internal node the heavier child
(the one whose Ershov number is larger) is scheduled first; when the two
children tie, commutative freedom allows either order. The task asks for the
minimum register count and the postorder sequence of node ids that realizes an
optimal order.
"""

import random

from reasoning_core.template import Config, Entry, Task


class ErshovConfig(Config):
    leaves: int = 6

    def apply_difficulty(self, level):
        self.leaves = 4 * (level + 3)


def _ershov_numbers(tree):
    """Return dict node_id -> Ershov number for a full binary tree."""
    nums = {}
    for node in tree:
        c = tree[node]
        if c is None:
            nums[node] = 1
        else:
            l, r = nums[c[0]], nums[c[1]]
            if l == r:
                nums[node] = l + 1
            else:
                nums[node] = max(l, r)
    return nums


def _optimal_order(tree, nums, root):
    """Return a postorder optimal evaluation, heavier (or tied, either) first."""
    order = []

    def visit(node):
        c = tree[node]
        if c is not None:
            l, r = c[0], c[1]
            if nums[l] >= nums[r]:
                first, second = l, r
            else:
                first, second = r, l
            visit(first)
            visit(second)
        order.append(node)

    visit(root)
    return order


class ErshovRegisterNumbering(Task):
    summary = (
        "Label full binary expression trees with distinct leaves via bottom-up "
        "Ershov numbers; at commutative nodes either heavier-first order is "
        "accepted; emit the minimal register count and an optimal postorder "
        "node sequence, heavier child first."
    )
    design_choice = (
        "Choice 1: Use only full binary trees with distinct leaves; Ershov "
        "number is computed bottom-up, and the optimal order is forced except "
        "at commutative nodes where either heavier-subtree-first order is "
        "accepted."
    )
    config_cls = ErshovConfig

    def generate_entry(self):
        leaves = self.config.leaves
        # Build a random full binary tree as nested parenthesization.
        # A full binary tree with L leaves has L-1 internal nodes.
        num_internal = leaves - 1

        # Generate a random rooted full binary tree via a recursive split.
        def build(remaining):
            # remaining: number of leaf positions to create
            if remaining == 1:
                return None
            left = random.randint(1, remaining - 1)
            right = remaining - left
            return (build(left), build(right))

        shape = build(leaves)

        # Assign distinct ids in preorder. A full binary tree with `leaves`
        # leaves has 2*leaves-1 nodes total.
        ids = list(range(1, 2 * leaves))
        node_id = 0

        def assign(node):
            nonlocal node_id
            node_id += 1
            this = ids[node_id - 1]
            if node is None:
                return (this, None)
            l = assign(node[0])
            r = assign(node[1])
            return (this, (l, r))

        root = assign(shape)
        tree = {}

        def flatten(nd):
            nid, children = nd
            if children is None:
                tree[nid] = None
            else:
                l = flatten(children[0])
                r = flatten(children[1])
                tree[nid] = (l, r)
            return nid

        flatten(root)
        root_id = root[0]

        # All leaves
        leaves_ids = [n for n in tree if tree[n] is None]
        internal_ids = [n for n in tree if tree[n] is not None]

        # Precompute Ershov numbers.
        nums = _ershov_numbers(tree)

        min_registers = nums[root_id]

        # Both optimal orders (heavier-first at every commutative node,
        # swapping the two tied children when they tie).
        order = _optimal_order(tree, nums, root_id)

        # Validate: the order is a valid postorder of this tree and contains
        # every node exactly once.
        seq = list(order)
        assert sorted(seq) == sorted(tree.keys()), "order must cover all nodes"
        assert len(seq) == len(set(seq)), "order must be a permutation"
        # Validate postorder property: every child precedes its parent.
        for nid in tree:
            c = tree[nid]
            if c is not None:
                li = seq.index(c[0])
                ri = seq.index(c[1])
                pi = seq.index(nid)
                assert li < pi and ri < pi, "children must precede parent"
        # Validate Ershov: simulate first-fit register reuse along the
        # heavier-first schedule; with the optimal order this reaches exactly
        # the Ershov number (Sethi-Ullman), never exceeding it.
        live = {}
        free = set()
        max_live = 0
        for nid in seq:
            c = tree[nid]
            if c is None:
                if free:
                    reg = min(free)
                    free.discard(reg)
                else:
                    reg = max_live
                    max_live += 1
                live[nid] = reg
            else:
                l, r = c[0], c[1]
                rl = live.pop(l)
                rr = live.pop(r)
                free.add(rr)
                live[nid] = rl
        assert max_live <= min_registers, "schedule exceeds claimed optimum"
        # And min_registers = root Ershov number (a lower bound), so equality
        # holds: recompute recursively as an independent check.
        def rec(nid):
            c = tree[nid]
            if c is None:
                return 1
            a = rec(c[0])
            b = rec(c[1])
            return a + 1 if a == b else max(a, b)
        assert min_registers == rec(root_id)
        assert min_registers == nums[root_id]

        assert min_registers >= 1
        assert isinstance(min_registers, int)

        metadata = {
            "tree": {str(k): v if v is None else (str(v[0]), str(v[1])) for k, v in tree.items()},
            "root": root_id,
            "leaves": [int(x) for x in leaves_ids],
            "internal": [int(x) for x in internal_ids],
            "ershov": {str(k): int(v) for k, v in nums.items()},
            "order": [int(x) for x in order],
            "min_registers": int(min_registers),
        }
        answer = ",".join(str(x) for x in order) + f"|{min_registers}"
        return Entry(metadata=metadata, answer=answer)

    def render_prompt(self, metadata):
        tree = metadata["tree"]

        def render(nid):
            cc = tree[str(nid)]
            if cc is None:
                return str(nid)
            l, r = cc
            return f"({render(l)} {render(r)})"

        expr = render(metadata["root"])
        return (
            f"An expression is evaluated on a machine where each live value "
            f"occupies one register and each binary operation needs both of "
            f"its operands already computed as it produces its result, "
            f"consuming the two operands' registers and producing one. "
            f"The expression tree is {expr}, where each id is a distinct "
            f"subexpression value. You may reorder the independent "
            f"subexpressions freely (they are independent), and at a node "
            f"whose two children need equally many registers you may evaluate "
            f"them in either order. Give the minimum number of registers "
            f"needed to evaluate the whole expression, and one postorder "
            f"sequence of node ids realizing that minimum, evaluating the "
            f"heavier child (more registers needed) first, ties in either "
            f"order. Answer as the comma-separated node sequence followed by "
            f"a vertical bar and the register count, e.g. 2,3,1|2."
        )

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        answer = answer.strip()
        if "|" not in answer:
            return 0.0
        seq_part, reg_part = answer.rsplit("|", 1)
        try:
            min_reg = int(reg_part.strip())
        except ValueError:
            return 0.0
        if min_reg != entry.metadata["min_registers"]:
            return 0.0
        seq = [x.strip() for x in seq_part.split(",") if x.strip() != ""]
        if len(seq) != len(set(seq)):
            return 0.0
        tree = entry.metadata["tree"]
        valid_ids = set(tree.keys())
        if set(seq) != valid_ids:
            return 0.0
        # Must be a valid postorder with heavier child first.
        nums = entry.metadata["ershov"]
        pos = {nid: i for i, nid in enumerate(seq)}
        for nid in tree:
            c = tree[nid]
            if c is not None:
                l, r = c[0], c[1]
                if not (pos[l] < pos[nid] and pos[r] < pos[nid]):
                    return 0.0
                if nums[l] > nums[r] and not (pos[l] < pos[r]):
                    return 0.0
                if nums[r] > nums[l] and not (pos[r] < pos[l]):
                    return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'ershov_register_numbering (draw 1 of 3)',
 'hypothesis': 'P012',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_shortcuts_fail_r1/ershov_register_numbering',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1277236794,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'},
                             'fallback_provider': 'inferx'}}}
