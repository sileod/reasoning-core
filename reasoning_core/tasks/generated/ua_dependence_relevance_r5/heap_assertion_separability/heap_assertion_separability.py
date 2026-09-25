import random

from reasoning_core.template import Config, Entry, Task


class HeapAssertionSeparabilityConfig(Config):
    max_cells: int = 3
    max_depth: int = 1

    def apply_difficulty(self, level):
        self.max_cells = min(2 + level, 8)
        self.max_depth = 1 + min(level, 3)


def _formula_to_str(node):
    kind = node[0]
    if kind == "emp":
        return "emp"
    if kind == "p":
        return f"cell {node[1]} is owned"
    if kind == "star":
        return f"({_formula_to_str(node[1])}) * ({_formula_to_str(node[2])})"
    if kind == "wand":
        return f"({_formula_to_str(node[1])}) -** ({_formula_to_str(node[2])})"
    if kind == "or":
        return f"({_formula_to_str(node[1])}) or ({_formula_to_str(node[2])})"
    if kind == "and":
        return f"({_formula_to_str(node[1])}) and ({_formula_to_str(node[2])})"
    raise ValueError(kind)


def _eval_formula(node, heap, n):
    kind = node[0]
    if kind == "emp":
        return heap == 0
    if kind == "p":
        return heap == (1 << node[1])
    full = (1 << n) - 1
    if kind == "star":
        a, b = node[1], node[2]
        sub = heap
        while True:
            if _eval_formula(a, sub, n) and _eval_formula(b, heap ^ sub, n):
                return True
            if sub == 0:
                break
            sub = (sub - 1) & heap
        return False
    if kind == "wand":
        a, b = node[1], node[2]
        comp_mask = full ^ heap
        r = comp_mask
        while True:
            if _eval_formula(a, r, n) and not _eval_formula(b, heap | r, n):
                return False
            if r == 0:
                break
            r = (r - 1) & comp_mask
        return True
    if kind == "or":
        return _eval_formula(node[1], heap, n) or _eval_formula(node[2], heap, n)
    if kind == "and":
        return _eval_formula(node[1], heap, n) and _eval_formula(node[2], heap, n)
    raise ValueError(kind)


def _build_formula(n, depth):
    if depth <= 0:
        if random.random() < 0.5:
            return ("p", random.randrange(n))
        return ("emp",)
    kind = random.choice(["star", "star", "star", "wand", "or", "and"])
    left = _build_formula(n, depth - 1)
    right = _build_formula(n, depth - 1)
    return (kind, left, right)


class HeapAssertionSeparability(Task):
    summary = "Evaluate spatial assertions over bounded heaps using disjoint ownership and separating implication; vary aliasing, nested connectives, and empty ownership; answer truth."
    design_choice = "fixed binary truth value with no witness, forcing solvers to decide satisfiability of the whole assertion over a given heap diagram."

    config_cls = HeapAssertionSeparabilityConfig

    def generate_entry(self):
        target = random.random() < 0.5
        for _ in range(300):
            n = self.config.max_cells
            heap_size = random.randint(1, n)
            heap = 0
            for c in random.sample(range(n), heap_size):
                heap |= 1 << c
            depth = random.randint(1, self.config.max_depth)
            formula = _build_formula(n, depth)
            truth = _eval_formula(formula, heap, n)
            if truth == target:
                return self._make_entry(n, heap, formula, truth)
        return self._make_entry(n, heap, formula, truth)

    def _make_entry(self, n, heap, formula, truth):
        cells = [i for i in range(n) if heap & (1 << i)]
        formula_str = _formula_to_str(formula)
        owned = ", ".join(str(c) for c in cells) if cells else "none"
        nset = ", ".join(str(i) for i in range(n))
        prompt = (
            f"Consider a heap over cell universe {{{nset}}}. "
            f"The current heap diagram allocates exactly the cells {{{owned}}}. "
            f"Decide whether the following spatial assertion holds over this heap. "
            f"The assertion is: {formula_str}. "
            f"Semantics: emp holds only on the empty heap; 'cell k is owned' holds only "
            f"when the heap is exactly {{k}}; P * Q holds when the heap splits into two "
            f"disjoint parts respectively satisfying P and Q; P -** Q holds when adding "
            f"any disjoint subheap satisfying P forces the result to satisfy Q. "
            f"Answer with a single word, indicating your decision."
        )
        answer = "true" if truth else "false"
        return Entry(
            metadata={
                "universe": n,
                "heap": cells,
                "formula": formula_str,
                "answer_value": int(truth),
                "_prompt": prompt,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        return metadata["_prompt"]

    def score_answer(self, answer, entry):
        if answer is None:
            return 0.0
        a = str(answer).strip().lower()
        if a == "true":
            gold = True
        elif a == "false":
            gold = False
        else:
            return 0.0
        return 1.0 if gold == entry.metadata["answer_value"] else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'heap_assertion_separability (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dependence_relevance_r5/heap_assertion_separability',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
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
