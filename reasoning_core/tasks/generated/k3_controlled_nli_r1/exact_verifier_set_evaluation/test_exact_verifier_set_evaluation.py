import json
import random
from itertools import product

import pytest

from reasoning_core.tasks.generated.k3_controlled_nli_r1.exact_verifier_set_evaluation.exact_verifier_set_evaluation import (
    ExactVerifierSetEvaluation,
    _evaluate,
    _render,
    _space,
    _verify_formula,
)
from reasoning_core.template import Entry


def test_exact_fusion_is_not_intersection():
    states = ["a", "b", "c", "d"]
    table = {a: {b: states[i | j] for j, b in enumerate(states)}
             for i, a in enumerate(states)}
    binding = {"p": ["b"], "q": ["c"], "r": ["a", "b"]}
    tree = ("∨", ("∧", "p", "q"), "r")
    assert _evaluate(tree, binding, table) == {"a", "b", "d"}
    assert _verify_formula(_render(tree), binding, table, states) == {"a", "b", "d"}
    assert _evaluate(("∧", "p", "p"), binding, table) == {"b"}


def test_all_bindings_and_operators_on_two_states():
    states = ["a", "b"]
    table = {"a": {"a": "a", "b": "b"}, "b": {"a": "b", "b": "b"}}
    subsets = [[], ["a"], ["b"], ["a", "b"]]
    for p, q, r, op1, op2 in product(subsets, subsets, subsets, ["∧", "∨"], ["∧", "∨"]):
        binding = {"p": p, "q": q, "r": r}
        for tree in [(op1, (op2, "p", "q"), "r"), (op1, "p", (op2, "q", "r"))]:
            assert _evaluate(tree, binding, table) == _verify_formula(_render(tree), binding, table, states)


@pytest.mark.parametrize("dimensions", [2, 3, 4])
def test_fusion_is_a_closed_semilattice(dimensions):
    for _ in range(5):
        states, table = _space(dimensions)
        for a, b, c in product(states, repeat=3):
            assert table[a][a] == a
            assert table[a][b] == table[b][a]
            assert table[table[a][b]][c] == table[a][table[b][c]]
            assert table[a][b] in states


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_generated_gold_and_json(level):
    task = ExactVerifierSetEvaluation()
    task.config.set_level(level)
    answers = set()
    for _ in range(12):
        entry = task.generate_entry()
        metadata = json.loads(json.dumps(entry.metadata))
        assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
        formula = metadata["formula"]
        assert "∧" in formula and "∨" in formula
        gold = _verify_formula(formula, metadata["subject_matter"], metadata["fusion_table"], metadata["states"])
        assert entry.answer == ", ".join(sorted(gold))
        assert task.score_answer(entry.answer, entry) == 1
        assert task.score_answer("", entry) == 0
        assert task.score_answer("not a state", entry) == 0
        answers.add(entry.answer)
    assert len(answers) > 1


def test_scorer_requires_sorted_unique_set_without_self():
    class NoAccess:
        def __getattribute__(self, name):
            raise AssertionError(name)

    score = ExactVerifierSetEvaluation.score_answer
    entry = Entry(metadata={}, answer="a, c")
    assert score(NoAccess(), "a,c", entry) == 1
    for bad in ["", "c, a", "a, a, c", "a", "a, c, d", "none", None, 2]:
        assert score(NoAccess(), bad, entry) == 0


def test_conjunction_of_an_atom_with_itself_can_add_states():
    states = ["a", "b", "c", "d"]
    table = {a: {b: states[i | j] for j, b in enumerate(states)}
             for i, a in enumerate(states)}
    binding = {"p": ["b", "c"]}
    tree = ("∧", "p", "p")
    assert _evaluate(tree, binding, table) == {"b", "c", "d"}
    assert _verify_formula(_render(tree), binding, table, states) == {"b", "c", "d"}
    assert _evaluate(("∨", "p", "p"), binding, table) == {"b", "c"}


def test_prompt_contains_every_gold_dependency():
    task = ExactVerifierSetEvaluation()
    task.config.set_level(6)
    for _ in range(10):
        entry = task.generate_entry()
        prompt = task.render_prompt(entry.metadata)
        grid = prompt.split("headers list all states):\n", 1)[1].split("\nSubject-matter map:\n", 1)[0]
        lines = grid.splitlines()
        states = lines[0].split()
        table = {}
        for line in lines[1:]:
            row, *cells = line.split()
            assert len(cells) == len(states)
            table[row] = dict(zip(states, cells))
        bindings = prompt.split("Subject-matter map:\n", 1)[1].split("\nFormula: ", 1)[0]
        binding = {}
        for line in bindings.splitlines():
            atom, values = line.split(" -> ")
            binding[atom] = values[1:-1].split(", ") if values[1:-1] else []
        formula = prompt.split("\nFormula: ", 1)[1].splitlines()[0]
        expected = _verify_formula(formula, binding, table, states)
        assert entry.answer == ", ".join(sorted(expected))


def test_fixed_seed_reproduces_entries():
    state = random.getstate()
    try:
        random.seed(682015719)
        task = ExactVerifierSetEvaluation()
        first = task.generate_entry()
        random.seed(682015719)
        task = ExactVerifierSetEvaluation()
        second = task.generate_entry()
        assert first.metadata == second.metadata
        assert first.answer == second.answer
    finally:
        random.setstate(state)
