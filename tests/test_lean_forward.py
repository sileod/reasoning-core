import networkx as nx

from reasoning_core import get_task, list_tasks
from reasoning_core.tasks.math_lean import (
    BANNED_LEAN_TOKENS,
    LeanConfig,
    gen_forward_order_graph,
    get_runner,
)


def test_get_task_loads_dev_tasks_without_listing_them():
    assert "lean_forward_proof" not in list_tasks()
    assert type(get_task("LeanForwardProof", use_mathlib=False)).__name__ == "LeanForwardProof"


def test_forward_graph_core_profile_verifies_and_is_well_formed():
    inst = gen_forward_order_graph(LeanConfig(use_mathlib=False))

    assert inst is not None
    assert nx.is_directed_acyclic_graph(inst.G)
    assert inst.stats.final_verifies
    assert inst.stats.proof_depth >= 3
    assert inst.stats.useful_premises >= 2
    assert not any(tok in inst.theorem.lower() for tok in BANNED_LEAN_TOKENS)
    assert get_runner(use_mathlib=False).check(inst.theorem)[0]

    seen = set(inst.leaf_hyp_names.values())
    for line in inst.proof.splitlines():
        if line.startswith("have "):
            name = line.split()[1]
            refs = {tok for tok in line.replace(":", " ").split() if tok.startswith("h") and tok[1:].isdigit()}
            assert refs - {name} <= seen
            seen.add(name)

    for node in inst.G.nodes:
        data = inst.G.nodes[node]["data"]
        assert data.clause_formula
        assert data.full_cnf_clause
        if inst.G.in_degree(node):
            assert data.inference
            assert set(data.parents) == set(inst.G.predecessors(node))


def test_forward_tasks_score_reference_answers():
    for name in ("LeanForwardProof", "LeanDerivationPremiseSelection"):
        task = get_task(name, use_mathlib=False)
        ex = task.generate_example(max_tokens=12000)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_missing_line_displays_unique_compiling_option():
    task = get_task("LeanMissingProofLine", use_mathlib=False)
    for _ in range(5):
        ex = task.generate_example(max_tokens=12000)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert ex.metadata.compiling_lines == [ex.answer]
        assert "omega" not in ex.metadata.available_lines
        assert "tauto" not in ex.metadata.available_lines
