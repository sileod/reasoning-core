import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding

TASK_META = {'parent_source_id': None,
 'idea': 'alphabeta_cutoff_trace (draw 2 of 3)',
 'hypothesis': 'P001',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_incremental_recomputation_r1/alphabeta_cutoff_trace',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
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


@dataclass
class AlphaBetaConfig(Config):
    depth: int = 3
    min_val: int = -9
    max_val: int = 9

    def apply_difficulty(self, level):
        self.depth = min(2 + level // 2, 5)


def _parse_tree_string(s):
    s = s.strip()
    stack = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == '(':
            stack.append([])
            i += 1
        elif c == ')':
            if len(stack) == 1:
                return stack.pop()
            child = stack.pop()
            stack[-1].append(child)
            i += 1
        elif c == ',' or c == ' ':
            i += 1
        elif c == '-':
            j = i + 1
            while j < n and s[j].isdigit():
                j += 1
            val = int(s[i:j])
            stack[-1].append(val)
            i = j
        elif c.isdigit():
            j = i
            while j < n and s[j].isdigit():
                j += 1
            val = int(s[i:j])
            stack[-1].append(val)
            i = j
        else:
            raise ValueError(f"unexpected char {c!r}")
    raise ValueError("unbalanced")


def _serialize(node):
    if isinstance(node, list):
        return f"({','.join(_serialize(c) for c in node)})"
    return str(node)


def _alphabeta_trace(root, maximizing_root):
    """Run alpha-beta. Returns (root_value, sorted list of pruned leaf values).
    maximizing_root is True. Leaves pruned = leaves never evaluated due to cutoff.
    """
    pruned = []

    def _leaves(node):
        if isinstance(node, int):
            return [node]
        acc = []
        for c in node:
            acc.extend(_leaves(c))
        return acc

    def rec(node, alpha, beta, maximizing):
        if isinstance(node, int):
            return node
        if maximizing:
            value = float('-inf')
            for child in node:
                if isinstance(child, int):
                    cv = child
                else:
                    cv = rec(child, alpha, beta, False)
                if cv > value:
                    value = cv
                if value >= beta:
                    for rest in node[node.index(child) + 1:]:
                        pruned.extend(_leaves(rest))
                    break
                if value > alpha:
                    alpha = value
            return value
        else:
            value = float('inf')
            for i, child in enumerate(node):
                if isinstance(child, int):
                    cv = child
                else:
                    cv = rec(child, alpha, beta, True)
                if cv < value:
                    value = cv
                if value <= alpha:
                    for rest in node[i + 1:]:
                        pruned.extend(_leaves(rest))
                    break
                if value < beta:
                    beta = value
            return value

    root_val = rec(root, float('-inf'), float('inf'), maximizing_root)
    pruned = sorted(pruned)
    # dedupe keeping sorted order
    dedup = []
    for v in pruned:
        if not dedup or dedup[-1] != v:
            dedup.append(v)
    return root_val, dedup


class AlphaBetaCutoffTraceV2(Task):
    task_name = "alpha_beta_cutoff_trace"
    summary = "Run alpha-beta over an explicit valued game tree with fixed move order, tracking the window and logging each cutoff; vary depth, branching, and ordering; answer is the root value and pruned-leaf set."
    design_choice = "Encode the tree as a compact string using parentheses and comma-separated integers (e.g., (5,(3,7),2)), with branching factor and depth implicit; the answer is the root value and a sorted list of pruned leaf values."
    config_cls = AlphaBetaConfig
    task_version = 2

    def generate_entry(self):
        cfg = self.config

        def build(depth_left):
            if depth_left == 0:
                return random.randint(cfg.min_val, cfg.max_val)
            branching = random.randint(2, 3)
            return [build(depth_left - 1) for _ in range(branching)]

        depth = cfg.depth
        root = build(depth)
        tree_str = _serialize(root)
        maximizing_root = True
        root_val, pruned = _alphabeta_trace(root, maximizing_root)
        root_val = int(root_val)
        pruned_str = ",".join(str(v) for v in pruned)
        answer = f"{root_val};{pruned_str}"
        assert isinstance(root_val, int)
        assert cfg.min_val <= root_val <= cfg.max_val
        return Entry(metadata={"tree": tree_str,
                               "maximizing_root": maximizing_root,
                               "depth": depth,
                               "root_value": root_val,
                               "pruned_leaves": pruned,
                               "answer": answer},
                     answer=answer)

    def render_prompt(self, metadata):
        return (f"Consider a game tree encoded as nested parentheses: "
                f"each tuple is an internal node whose children are listed left to right, "
                f"and leaves are integers. MAX nodes appear at even depth (the root, depth 0), "
                f"MIN nodes at odd depth. Run minimax with alpha-beta using a fixed left-to-right "
                f"move order, and record every leaf that is pruned by a cutoff (never evaluated). "
                f"The tree is {metadata['tree']}. "
                f"Report the root value and the sorted, comma-separated list of pruned leaf values "
                f"as 'root;leaf1,leaf2,...' (omit the list after the semicolon if no leaf is pruned).")

    def score_answer(self, answer, entry):
        return module_score_answer(answer, entry)


def module_score_answer(answer, entry):
    if answer is None:
        return 0.0
    a = str(answer).strip()
    gold = entry.answer
    if a == gold:
        return 1.0
    return 0.0
