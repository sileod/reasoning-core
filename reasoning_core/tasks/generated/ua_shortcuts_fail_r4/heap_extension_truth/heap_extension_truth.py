import itertools
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

NIL = "null"


@dataclass
class HeapExtensionTruthConfig(Config):
    n_labels: int = 3
    max_depth: int = 1
    max_attempts: int = 200

    def apply_difficulty(self, level):
        self.n_labels = 3 + (1 if level >= 2 else 0)
        self.max_depth = 1 + level // 2
        self.max_attempts = 200 + 50 * level


def _labels(n):
    return ["a", "b", "c", "d", "e"][:n]


class _BudgetExceeded(Exception):
    pass


_BUDGET = [0]


def _bump():
    _BUDGET[0] += 1
    if _BUDGET[0] > 60000:
        raise _BudgetExceeded()


def _all_heaps(labels):
    vals = list(labels) + [NIL]
    for size in range(0, len(labels) + 1):
        for dom in itertools.combinations(labels, size):
            for assign in itertools.product(vals, repeat=size):
                yield dict(zip(dom, assign))


def _random_heap(labels):
    h = {}
    for x in labels:
        if random.random() < 0.5:
            h[x] = random.choice(list(labels) + [NIL])
    return h


def _holds(f, h, labels):
    _bump()
    t = f[0]
    if t == "emp":
        return not h
    if t == "atom":
        x, y = f[1], f[2]
        return len(h) == 1 and x in h and h[x] == y
    if t == "conj":
        A, B = f[1], f[2]
        keys = list(h.keys())
        n = len(keys)
        for mask in range(1 << n):
            h1 = {}
            h2 = {}
            for i, k in enumerate(keys):
                if (mask >> i) & 1:
                    h1[k] = h[k]
                else:
                    h2[k] = h[k]
            if _holds(A, h1, labels) and _holds(B, h2, labels):
                return True
        return False
    if t == "wand":
        A, B = f[1], f[2]
        free = [x for x in labels if x not in h]
        return _wand(h, A, B, free, labels)


def _wand(h, A, B, free, labels, idx=0, acc=None):
    _bump()
    if acc is None:
        acc = {}
    if idx == len(free):
        if _holds(A, acc, labels):
            return _holds(B, dict(h, **acc), labels)
        return True
    x = free[idx]
    if not _wand(h, A, B, free, labels, idx + 1, acc):
        return False
    vals = list(labels) + [NIL]
    for val in vals:
        acc[x] = val
        if not _wand(h, A, B, free, labels, idx + 1, acc):
            return False
    acc.pop(x, None)
    return True


def _gen_atom(labels):
    x = random.choice(labels)
    y = random.choice(list(labels) + [NIL])
    return ("atom", x, y)


def _gen_formula(depth, labels):
    if depth <= 0 or random.random() < 0.35:
        if random.random() < 0.2:
            return ("emp",)
        return _gen_atom(labels)
    op = random.choice(["conj", "wand"])
    return (op, _gen_formula(depth - 1, labels), _gen_formula(depth - 1, labels))


def _render_formula(f):
    t = f[0]
    if t == "emp":
        return "emp"
    if t == "atom":
        return "%s -> %s" % (f[1], f[2])
    op = " * " if t == "conj" else " -* "
    return "(" + _render_formula(f[1]) + op + _render_formula(f[2]) + ")"


def _parse_truth(answer):
    if not isinstance(answer, str):
        return None
    s = answer.strip().lower()
    if s in ("true", "1", "yes"):
        return True
    if s in ("false", "0", "no"):
        return False
    return None


class HeapExtensionTruth(Task):
    summary = "Evaluate assertions on bounded heaps using points-to facts, separating conjunction, and separating implication; quantify over disjoint splits and extensions to return the assertion's truth value."
    design_choice = "Use heap graphs with fixed node labels; assertions combine points-to, disjointness, and extension; answer is true/false."
    config_cls = HeapExtensionTruthConfig

    def generate_entry(self):
        labels = _labels(self.config.n_labels)
        n_tries = max(60, 30 * (1 + self.config.max_depth))
        for _ in range(self.config.max_attempts):
            f = _gen_formula(self.config.max_depth, labels)
            _BUDGET[0] = 0
            found_true = False
            found_false = False
            h_true = None
            h_false = None
            try:
                for _ in range(n_tries):
                    h = _random_heap(labels)
                    if _holds(f, h, labels):
                        if not found_true:
                            h_true = h
                            found_true = True
                    else:
                        if not found_false:
                            h_false = h
                            found_false = True
                    if found_true and found_false:
                        break
            except _BudgetExceeded:
                continue
            if not (found_true and found_false):
                continue
            if random.random() < 0.5:
                chosen = h_true
            else:
                chosen = h_false
            _BUDGET[0] = 0
            try:
                result = _holds(f, chosen, labels)
            except _BudgetExceeded:
                continue
            if result != (chosen is h_true):
                continue
            return Entry(
                metadata={
                    "n_labels": len(labels),
                    "labels": labels,
                    "heap": dict(sorted(chosen.items(), key=lambda kv: kv[0])),
                    "formula": _render_formula(f),
                    "answer": result,
                },
                answer="True" if result else "False",
            )
        raise RuntimeError(
            "HeapExtensionTruth: no assertion with both a satisfying and a refuting "
            "heap found after bounded attempts"
        )

    def render_prompt(self, metadata):
        heap = metadata["heap"]
        if not heap:
            heap_str = "the heap is empty"
        else:
            heap_str = "; ".join("%s -> %s" % (k, v) for k, v in heap.items())
        return (
            "Consider a heap whose locations are drawn from the set {%s}, where each "
            "location has at most one outgoing pointer, and a pointer may target any "
            "location in the set or the special value null. The heap is described by "
            "listing its points-to facts; any location not listed has no outgoing pointer.\n"
            "\n"
            "The heap is: %s\n"
            "\n"
            "Separation-logic semantics: the points-to fact 'x -> y' holds exactly in the "
            "one-pointer heap whose only pointer is x -> y. 'emp' holds in the empty heap "
            "(no pointers). A * B holds iff the heap can be split into two disjoint heaps "
            "(disjoint sets of locations holding pointers) with one satisfying A and the "
            "other satisfying B. A -* B holds iff for every heap h' disjoint from the "
            "current heap (built only from locations that currently hold no pointer here) "
            "that satisfies A, merging h' into the current heap yields a heap satisfying B.\n"
            "\n"
            "Decide whether the following assertion is true of the given heap, and state "
            "your conclusion as exactly the single word 'true' or 'false'.\n"
            "\n"
            "Assertion: %s"
        ) % (", ".join(metadata["labels"]), heap_str, metadata["formula"])

    def score_answer(self, answer, entry):
        parsed = _parse_truth(answer)
        if parsed is None:
            return 0.0
        return 1.0 if parsed == entry.metadata["answer"] else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'heap_extension_truth (variant 1 of 3)',
 'hypothesis': 'P007',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_shortcuts_fail_r4/heap_extension_truth',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1139467751,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
