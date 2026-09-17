import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'exact_verifier_set_evaluation (variant 1 of 3)',
 'hypothesis': 'P008',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/k3_controlled_nli_r1/exact_verifier_set_evaluation',
 'generation': {'provider_name': 'orfree',
                'model_name': 'stealth/union-alpha',
                'harness_name': 'opencode',
                'harness_version': '1.18.31',
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


@dataclass
class VerifierSetConfig(Config):
    dimensions: int = 2
    num_atoms: int = 3
    formula_leaves: int = 3

    def apply_difficulty(self, level):
        self.dimensions = min(4, 2 + int(level) // 3)
        self.num_atoms = min(8, 3 + int(level) // 2)
        self.formula_leaves = min(15, 3 + 2 * int(level))


def _formula(atoms, leaves):
    if leaves == 1:
        return random.choice(atoms)
    split = random.randint(1, leaves - 1)
    return (random.choice(["∧", "∧", "∨"]),
            _formula(atoms, split), _formula(atoms, leaves - split))


def _render(node):
    if isinstance(node, str):
        return node
    op, left, right = node
    return f"({_render(left)} {op} {_render(right)})"


def _evaluate(node, binding, table):
    if isinstance(node, str):
        return set(binding[node])
    op, left, right = node
    ls = _evaluate(left, binding, table)
    rs = _evaluate(right, binding, table)
    return ls | rs if op == "∨" else {table[a][b] for a in ls for b in rs}


def _verify_formula(text, binding, table, states):
    tokens = text.replace("(", "( ").replace(")", " )").split()
    stack = []
    for token in tokens:
        if token != ")":
            stack.append(tuple(s in binding[token] for s in states)
                         if token in binding else token)
            continue
        right, op, left, opening = (stack.pop() for _ in range(4))
        assert opening == "(" and op in ("∧", "∨")
        result = tuple(
            (left[k] or right[k]) if op == "∨" else any(
                left[i] and right[j] and table[a][b] == state
                for i, a in enumerate(states) for j, b in enumerate(states)
            )
            for k, state in enumerate(states)
        )
        stack.append(result)
    assert len(stack) == 1 and isinstance(stack[0], tuple)
    return {state for state, present in zip(states, stack[0]) if present}


def _space(dimensions):
    masks = {0, 1, 2, 3, (1 << dimensions) - 1}
    masks.update(random.sample(range(1 << dimensions), random.randint(1, dimensions + 1)))
    while True:
        extended = masks | {a | b for a in masks for b in masks}
        if extended == masks:
            break
        masks = extended
    labels = random.sample("abcdefghijklmnopqrstuvwx", len(masks))
    names = dict(zip(sorted(masks), labels))
    states = sorted(labels)
    table = {names[a]: {names[b]: names[a | b] for b in sorted(masks)}
             for a in sorted(masks)}
    assert all(table[a][a] == a and table[a][b] in states and table[a][b] == table[b][a]
               for a in states for b in states)
    return states, table


class ExactVerifierSetEvaluation(Task):
    summary = "State spaces with a given fusion table and subject-matter map: evaluate formulas by exact-verification clauses (atoms by stated relevance, conjunction by fusion, disjunction by union); return the sorted verifier set."
    design_choice = "Instance format: provide the fusion table as a 2D grid of labels and the subject-matter map as a list of atom-to-set bindings; the formula is a parenthesized expression with ∧ and ∨."
    config_cls = VerifierSetConfig
    task_version = 3

    def generate_entry(self):
        states, table = _space(self.config.dimensions)
        atoms = [f"p{i}" for i in range(self.config.num_atoms)]
        for _ in range(100):
            binding = {atom: sorted(random.sample(states, random.randint(1, min(3, len(states) - 1))))
                       for atom in atoms}
            tree = _formula(atoms, random.randint(3, self.config.formula_leaves))
            formula = _render(tree)
            target = _evaluate(tree, binding, table)
            if "∧" in formula and "∨" in formula and target and len(target) < len(states):
                break
        else:
            raise RuntimeError("could not generate a mixed exact-verification formula")
        verified = _verify_formula(formula, binding, table, states)
        assert target == verified and target <= set(states)
        answer = ", ".join(sorted(target))
        assert set(answer.split(", ")) == verified
        return Entry(metadata={"states": states, "fusion_table": table,
                               "subject_matter": binding, "formula": formula}, answer=answer)

    def render_prompt(self, metadata):
        states = metadata["states"]
        table = metadata["fusion_table"]
        rows = ["    " + " ".join(states)]
        rows.extend(a + "   " + " ".join(table[a][b] for b in states) for a in states)
        bindings = "\n".join(f"{a} -> {{{', '.join(values)}}}"
                             for a, values in sorted(metadata["subject_matter"].items()))
        return (
            "Evaluate exact verification in this finite state space. The subject-matter map "
            "lists exactly the states relevant to each atom; these are its exact verifiers.\n"
            "Use bottom-up set evaluation: V(A ∧ B) = {fusion(x,y): x in V(A), y in V(B)}; "
            "V(A ∨ B) = V(A) union V(B). Conjunction is NOT intersection. "
            "Use only these clauses; add no other states. Repeated results count once.\n"
            "Fusion table (left state's row, right state's column; headers list all states):\n"
            + "\n".join(rows) + "\nSubject-matter map:\n" + bindings
            + "\nFormula: " + metadata["formula"]
            + "\nReturn the verifier states in lexicographic order, separated by commas and "
            "single spaces. Format example: a, c, d. For an empty set write none."
        )

    def score_answer(self, answer, entry):
        if not isinstance(answer, str) or not answer.strip():
            return 0.0
        got = [s.strip() for s in answer.strip().split(",")]
        return float(got == entry.answer.split(", "))
