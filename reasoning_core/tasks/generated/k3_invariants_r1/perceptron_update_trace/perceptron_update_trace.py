import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'perceptron_update_trace (draw 2 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_invariants_r1/perceptron_update_trace',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1705404348,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


@dataclass
class PerceptronTraceConfig(Config):
    feature_dim: int = 2
    num_examples: int = 4
    value_range: int = 2
    max_epochs: int = 3
    target_attempts: int = 60

    def apply_difficulty(self, level):
        self.feature_dim = 2 + level // 2
        self.num_examples = 4 + level
        self.value_range = 2 + level // 2
        self.max_epochs = 3 + level


def _run_trace(examples, max_epochs):
    d = len(examples[0][0])
    w = [0] * d
    last = -1
    for _ in range(max_epochs):
        first = -1
        for idx, (x, lbl) in enumerate(examples):
            if sum(wi * xi for wi, xi in zip(w, x)) * lbl <= 0:
                if first < 0:
                    first = idx
                w = [wi + lbl * xi for wi, xi in zip(w, x)]
        if first < 0:
            return -1, True
        last = first
    return last, False


def _random_data(d, n, vr):
    return [
        ([random.randint(-vr, vr) for _ in range(d)], random.choice([-1, 1]))
        for _ in range(n)
    ]


def _separable_data(d, n, vr):
    wt = [random.randint(1, 5) * random.choice([-1, 1]) for _ in range(d)]
    out = []
    while len(out) < n:
        x = [random.randint(-vr, vr) for _ in range(d)]
        dot = sum(a * b for a, b in zip(wt, x))
        if dot == 0:
            continue
        out.append((x, 1 if dot > 0 else -1))
    return out


class PerceptronUpdateTrace(Task):
    summary = ("Execute perceptron mistake updates over ordered integer feature-label "
               "pairs, cycling until convergence or a stated pass cap; return the first "
               "example index (0-based) that causes a mistake in the final epoch, or -1 "
               "if none.")
    design_choice = ("Return the first example index (0-based) that causes a mistake in "
                     "the final epoch, or -1 if none.")
    config_cls = PerceptronTraceConfig

    def generate_entry(self):
        c = self.config
        n = c.num_examples
        d = c.feature_dim
        vr = c.value_range
        target = random.randrange(-1, n)
        ans = None
        attempts = 0
        while attempts < c.target_attempts:
            attempts += 1
            if target == -1:
                examples = _separable_data(d, n, vr)
            else:
                examples = _random_data(d, n, vr)
            a, _converged = _run_trace(examples, c.max_epochs)
            if a == target:
                ans = a
                break
            if a == -1 and target == -1:
                pass
        if ans is None:
            examples = _random_data(d, n, vr)
            ans, _c = _run_trace(examples, c.max_epochs)
        if not -1 <= ans < n:
            raise RuntimeError("perceptron trace produced out-of-domain first-mistake index")
        metadata = {
            "feature_dim": d,
            "num_examples": n,
            "value_range": vr,
            "max_epochs": c.max_epochs,
            "examples": [[list(x), lbl] for (x, lbl) in examples],
            "final_first_mistake": ans,
        }
        return Entry(metadata=metadata, answer=str(ans))

    def render_prompt(self, metadata):
        m = metadata
        ex_lines = [
            "example %d: features %s, label %d" % (i, x, lbl)
            for i, (x, lbl) in enumerate(m["examples"])
        ]
        xarr = "\n".join(ex_lines)
        return (
            "Run the standard perceptron algorithm on the following ordered integer "
            "feature-label pairs. Initialize the weights to the zero vector (no bias). "
            "In each epoch scan the examples in the order shown; for (x, y) it is a "
            "mistake when y*(w dot x) <= 0, and then update w := w + y*x. Run for at "
            "most %d epochs, stopping early if an entire epoch makes zero mistakes. "
            "Report the 0-based index of the FIRST example that causes a mistake in the "
            "final epoch that is run, or -1 if that final epoch has no mistakes (the "
            "algorithm converged). For example, if the first mistake in the final epoch "
            "is the example at index 2, answer 2.\n\n"
            "%s\n\n"
            "Answer as a single integer."
            % (m["max_epochs"], xarr)
        )

    def score_answer(self, answer, entry):
        try:
            return 1.0 if int(str(answer).strip()) == int(entry.answer) else 0.0
        except ValueError:
            return 0.0
