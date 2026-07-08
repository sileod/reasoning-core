import networkx as nx
import numpy as np

from reasoning_core.tasks.qualitative_causal_reasoning import (
    KERNELS,
    LABELS,
    QualitativeCausalReasoning,
    Query,
    add_edge,
    kernel_blocked_mediator,
    kernel_competing_paths,
    kernel_closed_collider,
    kernel_common_cause,
    kernel_observe_vs_do_association,
    kernel_observe_vs_do_intervention,
    kernel_open_collider,
    kernel_reverse_path,
    sample_instance,
    verify,
    verify_association,
    verify_intervention,
)


def test_direct_positive():
    G = nx.DiGraph()
    add_edge(G, "X", "Y", "+")
    q = Query("intervention", "X", "Y")
    assert verify_intervention(G, q) == "increase"


def test_direct_negative():
    G = nx.DiGraph()
    add_edge(G, "X", "Y", "-")
    q = Query("intervention", "X", "Y")
    assert verify_intervention(G, q) == "decrease"


def test_competing_paths_ambiguous():
    G, q = kernel_competing_paths(np.random.default_rng(0))
    assert verify_intervention(G, q) == "ambiguous"


def test_blocked_mediator():
    G, q = kernel_blocked_mediator(np.random.default_rng(0))
    assert verify_intervention(G, q) == "no_effect"


def test_do_removes_incoming_edges():
    G = nx.DiGraph()
    add_edge(G, "Z", "X", "+")
    add_edge(G, "Z", "Y", "+")
    q = Query("intervention", "X", "Y")
    assert verify_intervention(G, q) == "no_effect"


def test_common_cause_association():
    G, q = kernel_common_cause("increase", np.random.default_rng(0))
    assert verify_association(G, q) == "increase"


def test_closed_collider_blocks_association():
    G, q = kernel_closed_collider(np.random.default_rng(0))
    assert verify_association(G, q) == "no_effect"


def test_open_collider_explaining_away_decreases():
    G, q = kernel_open_collider(np.random.default_rng(0))
    assert verify_association(G, q) == "decrease"


def test_observation_vs_intervention_contrast():
    G, q = kernel_observe_vs_do_association(np.random.default_rng(0))
    assert verify(G, q) == "increase"

    G, q = kernel_observe_vs_do_intervention(np.random.default_rng(0))
    assert verify(G, q) == "no_effect"


def test_reverse_path_no_intervention_effect():
    G, q = kernel_reverse_path(np.random.default_rng(0))
    assert verify(G, q) == "no_effect"


def test_sample_instance_is_deterministic_and_verified():
    a = sample_instance(seed=123)
    b = sample_instance(seed=123)

    assert a.answer == b.answer
    assert sorted(a.graph.edges(data="sign")) == sorted(b.graph.edges(data="sign"))
    assert a.query == b.query
    assert verify(a.graph, a.query) == a.answer


def test_task_generate_example_scores_and_prompts():
    task = QualitativeCausalReasoning()
    problem = task.generate_example(max_tokens=0)

    assert problem.answer in {"increase", "decrease", "no_effect", "ambiguous"}
    assert problem.metadata.query_kind in {"intervention", "association"}
    assert "Answer with one of: increase, decrease, no_effect, ambiguous." in problem.prompt
    assert task.score_answer(problem.answer, problem) == 1
    assert task.score_answer("not_a_label", problem) == 0


def test_each_kernel_declares_exact_reachable_labels():
    rng = np.random.default_rng(0)
    all_labels = set()

    for labels, make in KERNELS.values():
        all_labels.update(labels)
        for label in labels:
            G, q = make(label, rng)
            assert verify(G, q) == label

    assert all_labels == set(LABELS)
