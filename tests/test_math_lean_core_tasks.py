import ast

import networkx as nx

from reasoning_core.template import Problem, edict
from reasoning_core.tasks import math_lean as ml


def _fake_compile_instance():
    return edict(
        kind="core_prop_chain",
        header="theorem ex (p q : Prop) (h0 : p → q) : p → q := by\n",
        candidates=["rfl", "exact h0", "intro hp; exact h0 hp", "simp"],
        labels=[False, True, True, False],
        primary="exact h0",
        elegant="exact h0",
        use_mathlib=False,
    )


def _fake_nondiscriminative_instance():
    return edict(
        kind="poly_eq",
        header="theorem ex (a : Int) : a + 0 = a := by\n",
        candidates=["ring", "simp", "rfl"],
        labels=[True, True, False],
        primary="ring",
        elegant="ring",
        use_mathlib=True,
    )


def _fake_derivation_instance():
    G = nx.DiGraph()

    def add(node, formula, parents=(), depth=0):
        G.add_node(
            node,
            data=ml.LeanDerivationNode(
                clause_id=node,
                clause_formula=formula,
                parents=tuple(parents),
                inference="hypothesis" if not parents else "Int.le_trans",
                role="axiom" if not parents else "plain",
                full_cnf_clause=f"cnf({node},plain,{formula})",
                proof="Int.le_trans {0} {1}" if parents else node,
                depth=depth,
            ),
        )
        for parent in parents:
            G.add_edge(parent, node)

    add("p0", "a ≤ b")
    add("p1", "b ≤ c")
    add("p2", "x ≤ y")
    add("p3", "u ≤ v")
    add("c4", "a ≤ c", ("p0", "p1"), 1)
    add("c5", "a ≤ c", ("c4",), 2)
    add("c6", "a ≤ c", ("c5",), 3)
    return edict(
        G=G,
        target_node="c6",
        goal="a ≤ c",
        proof="exact h4",
        stats=edict(proof_depth=3, useful_premises=2, total_premises=4, distractor_premises=2),
    )


def test_compile_selection_indices_generate_is_short_and_canonical(monkeypatch):
    monkeypatch.setattr(ml, "make_instance", lambda config: _fake_compile_instance())
    task = ml.LeanCompileSelectionIndices(ml.LeanConfig(use_mathlib=False))

    ex = task.generate()

    assert isinstance(ex, Problem)
    assert ex.answer == "[2, 3]"
    assert ast.literal_eval(ex.answer) == [i + 1 for i, ok in enumerate(ex.metadata.labels) if ok]
    assert "\n" not in ex.answer
    prompt = task.prompt(ex.metadata)
    assert "Do not copy proof bodies" in prompt
    assert task.score_answer("[2, 3]", ex) == 1.0


def test_compile_selection_retries_until_discriminative(monkeypatch):
    instances = iter([_fake_nondiscriminative_instance(), _fake_compile_instance()])
    monkeypatch.setattr(ml, "make_instance", lambda config: next(instances))
    task = ml.LeanCompileSelectionIndices(ml.LeanConfig(use_mathlib=False))

    ex = task.generate()

    assert ex.metadata.kind == "core_prop_chain"
    assert ex.answer == "[2, 3]"


def test_candidate_compilation_generate_returns_problem(monkeypatch):
    monkeypatch.setattr(ml, "make_instance", lambda config: _fake_compile_instance())
    task = ml.LeanCandidateCompilation(ml.LeanConfig(use_mathlib=False))

    ex = task.generate()

    assert isinstance(ex, Problem)
    assert ex.answer in {"True", "False"}
    assert len(ex.answer) <= 5


def test_candidate_compilation_does_not_require_discriminative_selection(monkeypatch):
    monkeypatch.setattr(ml, "make_instance", lambda config: _fake_nondiscriminative_instance())
    task = ml.LeanCandidateCompilation(ml.LeanConfig(use_mathlib=True))

    ex = task.generate()

    assert isinstance(ex, Problem)
    assert ex.metadata.kind == "poly_eq"


def test_derivation_premise_selection_answer_is_visible_leaf_reachability(monkeypatch):
    monkeypatch.setattr(ml, "gen_forward_order_graph", lambda config: _fake_derivation_instance())
    task = ml.LeanDerivationPremiseSelection(ml.LeanConfig(use_mathlib=False))

    ex = task.generate()

    assert isinstance(ex, Problem)
    assert ex.answer == "[1, 2]"
    leaf_nodes = [a.node for a in ex.metadata.axiom_nodes]
    ancestors = nx.ancestors(_fake_derivation_instance().G, ex.metadata.target_node)
    assert ast.literal_eval(ex.answer) == [i + 1 for i, n in enumerate(leaf_nodes) if n in ancestors]
    assert "\n" not in ex.answer

    prompt = task.prompt(ex.metadata)
    shown_nodes = {row.split(":", 1)[0] for row in ex.metadata.graph_rows}
    assert "..." not in prompt
    for row in ex.metadata.graph_rows:
        parents = row.rsplit("parents:", 1)[1].rstrip("]")
        if parents.strip() == "none":
            continue
        for parent in [p.strip() for p in parents.split(",")]:
            assert parent in shown_nodes
            assert parent in prompt


def test_core_lean_tasks_are_registered_and_dev_tasks_are_demoted():
    from reasoning_core import DATASETS, DEV_DATASETS

    assert {
        "lean_candidate_compilation",
        "lean_compile_selection_indices",
        "lean_derivation_premise_selection",
    } <= set(DATASETS)
    assert "lean_proof_repair" in DEV_DATASETS
    assert "lean_missing_proof_line" in DEV_DATASETS
    assert "lean_compile_selection" not in DATASETS
    assert "lean_forward_premise_selection" not in DATASETS
