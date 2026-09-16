import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


@dataclass
class SegmentTreeLazyPropagationConfig(Config):
    size: int = 5
    n_queries: int = 2
    max_intervals: int = 1

    def apply_difficulty(self, level):
        self.size = min(40, 5 + 2 * level)
        self.n_queries = 2 + level
        self.max_intervals = 1 if level < 2 else 3


class SegmentTreeLazyPropagation(Task):
    summary = "Interleave range-add and range-assign updates with sum/min range queries on a lazy segment tree: tags stack on shared nodes and flush only on descent; vary array sizes and interval shapes; answer every queried value."
    design_choice = "Instance format: fixed-size array with updates and queries given as explicit (l,r,op,val) triples; answer is a single integer per query, with 1-based inclusive intervals."
    config_cls = SegmentTreeLazyPropagationConfig

    def generate_entry(self):
        n = self.config.size
        vals = [random.randint(-20, 20) for _ in range(n)]
        ops = []
        for _ in range(self.config.n_queries):
            k = random.randint(1, self.config.max_intervals)
            for _ in range(k):
                l = random.randint(1, n)
                r = random.randint(l, n)
                op = random.choice(["add", "set"])
                val = random.randint(-20, 20)
                ops.append((l, r, op, val))
            qt = random.choice(["sum", "min"])
            ql = random.randint(1, n)
            qr = random.randint(ql, n)
            ops.append((ql, qr, qt, None))

        arr = list(vals)
        answers = []
        for op in ops:
            l, r, typ, val = op
            if typ == "add":
                for i in range(l - 1, r):
                    arr[i] += val
            elif typ == "set":
                for i in range(l - 1, r):
                    arr[i] = val
            elif typ == "sum":
                answers.append(sum(arr[l - 1:r]))
            else:
                answers.append(min(arr[l - 1:r]))

        seq = [(op[0], op[1], op[2], op[3]) for op in ops]
        return Entry(
            metadata={"n": n, "init": vals, "ops": seq, "answers": answers,
                      "cot": str(list(arr))},
            answer=";".join(str(a) for a in answers),
        )

    def render_prompt(self, metadata):
        lines = [f"The array has size {metadata['n']} with 1-based inclusive intervals.",
                 f"Initial: {metadata['init']}"]
        for op in metadata["ops"]:
            l, r, typ, val = op
            if typ in ("add", "set"):
                lines.append(f"Apply range-{typ} of {val} to [{l},{r}].")
            else:
                lines.append(f"Query range-{typ} on [{l},{r}].")
        lines.append("Answer is a single integer per query, in query order, separated by semicolons.")
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        answers = entry.metadata["answers"]
        if not isinstance(answer, str):
            return 0.0
        parts = answer.strip().split(";")
        if len(parts) != len(answers):
            return 0.0
        for p, a in zip(parts, answers):
            try:
                if int(p) != int(a):
                    return 0.0
            except ValueError:
                return 0.0
        return 1.0


TASK_META = {'parent_source_id': None,
 'idea': 'segment_tree_lazy_propagation (draw 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_dynamic_structures_r1/segment_tree_lazy_propagation',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
