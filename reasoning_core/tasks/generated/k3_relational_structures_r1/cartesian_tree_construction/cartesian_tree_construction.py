import random

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'cartesian_tree_construction (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_relational_structures_r1/cartesian_tree_construction',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


class CartesianTreeConfig(Config):
    length: int = 5
    max_val: int = 10
    tie_prob: float = 0.3

    def apply_difficulty(self, level):
        self.length = int(5 + level * 2)
        self.max_val = max(3, int(4 + level * 3))
        self.tie_prob = 0.25 + 0.1 * level


def _inorder_equals(vals, parent):
    n = len(vals)
    left = [-1] * n
    right = [-1] * n
    for i in range(n):
        p = parent[i]
        if p == -1:
            continue
        if i < p:
            left[p] = i
        else:
            right[p] = i
    roots = [i for i in range(n) if parent[i] == -1]
    if len(roots) != 1:
        return False
    out = []

    def walk(node):
        if node == -1:
            return
        walk(left[node])
        out.append(vals[node])
        walk(right[node])

    walk(roots[0])
    return out == vals


class CartesianTreeConstruction(Task):
    summary = ("Build the min- or max-Cartesian tree of an array whose inorder traversal "
               "returns the array, using a monotone stack of nearest smaller or greater "
               "neighbors; vary ties via strict or non-strict comparison; the answer is each "
               "element's parent index and the root.")
    config_cls = CartesianTreeConfig
    design_choice = ("Tie-breaking rule: use strict comparison for min-tree so equal values "
                     "make the left occurrence the parent, or use non-strict so the right "
                     "occurrence is parent; vary this between instances.")

    def generate_entry(self):
        cfg = self.config
        n = cfg.length
        while True:
            arr = [random.randint(0, cfg.max_val) for _ in range(n)]
            if len(set(arr)) < n:
                break
        mode = random.choice(["min", "max"])
        tie_strict = random.random() < 0.5
        parent = [-1] * n
        stack = []
        for i in range(n):
            last = -1
            while stack:
                j = stack[-1]
                if mode == "min":
                    better = arr[i] < arr[j] if tie_strict else arr[i] <= arr[j]
                else:
                    better = arr[i] > arr[j] if tie_strict else arr[i] >= arr[j]
                if not better:
                    break
                last = stack.pop()
            if stack:
                parent[i] = stack[-1]
            if last != -1:
                parent[last] = i
            stack.append(i)
        root = stack[0]
        assert _inorder_equals(arr, parent), "inorder reconstruction failed"
        answer_parts = [str(parent[i]) for i in range(n)]
        answer_parts.append(str(root))
        answer = " ".join(answer_parts)
        return Entry(metadata={
            "array": arr,
            "mode": mode,
            "tie_strict": tie_strict,
            "parent": parent,
            "root": root,
        }, answer=answer)

    def render_prompt(self, metadata):
        mode_word = "min" if metadata["mode"] == "min" else "max"
        if metadata["tie_strict"]:
            ties = ("a strict comparison, so among equal values the earlier (left) element "
                    "becomes the parent")
        else:
            ties = ("a non-strict comparison, so among equal values the later (right) element "
                    "becomes the parent")
        arr = metadata["array"]
        return (f"Given the array {arr}, build the {mode_word}-Cartesian tree using a monotone "
                f"stack with {ties}. The inorder traversal of the resulting tree equals the "
                f"array itself. Answer with each element's parent index (0-indexed, -1 if "
                f"none) in array order, then the root index, all space-separated.")

    def score_answer(self, answer, entry):
        expected = entry.answer
        if not isinstance(answer, str):
            return 0.0
        norm = " ".join(answer.split())
        return 1.0 if norm == expected else 0.0
