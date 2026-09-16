import random

from reasoning_core.template import Config, Entry, Task


class RecursionTreeCostConfig(Config):
    max_depth: int = 3
    split_family: int = 0

    def apply_difficulty(self, level):
        self.max_depth = 3 + level
        self.split_family = level


class RecursionTreeCostAnalysis(Task):
    summary = (
        "Expand divide-and-conquer recurrences into full call trees over concrete sizes "
        "with floor/ceil splits and per-node work terms, then sum work level by level; "
        "branching and split shapes vary; answer is the exact total."
    )
    design_choice = (
        "Choose per-node work as a power-of-two multiple of the node's input size, so "
        "level sums form geometric series with closed-form totals."
    )
    config_cls = RecursionTreeCostConfig

    def generate_entry(self):
        while True:
            n0 = random.randint(2, 12)
            b = random.choice([2, 3])
            if self.config.split_family >= 3:
                split_mode = random.choice(["floor", "ceil"])
            elif self.config.split_family >= 1:
                split_mode = random.choice(["equal", "ceil"])
            else:
                split_mode = "equal"

            work_mult = random.choice([1, 2, 4, 8])
            base_cost = random.choice([0, 1, 2, 4])

            sizes = {}
            _expand(n0, b, split_mode, 0, self.config.max_depth, sizes)

            total = 0
            for key, count in sizes.items():
                n = int(key.split(":")[1])
                total += _node_work(n, work_mult, base_cost) * count

            assert total >= 0
            return Entry(
                metadata={
                    "n0": n0,
                    "b": b,
                    "split_mode": split_mode,
                    "work_mult": work_mult,
                    "base_cost": base_cost,
                    "sizes": sizes,
                    "total": int(total),
                },
                answer=str(total),
            )

    def render_prompt(self, metadata):
        n0 = metadata["n0"]
        b = metadata["b"]
        split_mode = metadata["split_mode"]
        work_mult = metadata["work_mult"]
        base_cost = metadata["base_cost"]

        if split_mode == "equal":
            split_txt = f"each of size n//{b}"
        elif split_mode == "floor":
            split_txt = f"each of size n//{b} (floor)"
        else:
            split_txt = f"each of size ceil(n/{b})"

        return (
            f"Consider a divide-and-conquer recurrence on a problem of size {n0}. "
            f"Every node of size n spawns {b} child nodes, {split_txt}. "
            "A node of size 0 or 1 is a leaf and spawns no children. "
            f"Every node of size n contributes work equal to {work_mult}*n + {base_cost}. "
            f"Build the full recursion tree and compute the total work summed over all "
            f"nodes in the tree. What is the exact total? Answer with one integer."
        )

    def score_answer(self, answer, entry):
        try:
            val = float(answer.strip())
        except Exception:
            return 0.0
        if float(entry.answer) == val:
            return 1.0
        return 0.0


def _expand(n, b, split_mode, depth, max_depth, counts):
    key = f"{depth}:{n}"
    counts[key] = counts.get(key, 0) + 1
    if depth >= max_depth:
        return
    if n <= 1:
        return
    for _ in range(b):
        if split_mode == "ceil":
            child = (n + b - 1) // b
        else:
            child = n // b
        _expand(child, b, split_mode, depth + 1, max_depth, counts)


def _node_work(n, work_mult, base_cost):
    return work_mult * n + base_cost


TASK_META = {'parent_source_id': None,
 'idea': 'recursion_tree_cost_analysis (draw 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_hierarchical_recursive_r1/recursion_tree_cost_analysis',
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
