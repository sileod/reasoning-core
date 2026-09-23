import itertools

import pytest

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.parsimony_ancestral_state_inference.parsimony_ancestral_state_inference import (
    ParsimonyAncestralStateInference,
    _fitch_upward,
)


@pytest.fixture
def task():
    return ParsimonyAncestralStateInference()


def _bruteforce(tip_labels, children, root, n_tips, n_states):
    internal = [v for v in children if children[v]]
    best = None
    valid_roots = set()
    for assign in itertools.product(range(n_states), repeat=len(internal)):
        state = {}
        for a, v in zip(assign, internal):
            state[v] = a
        for t in range(n_tips):
            state[t] = tip_labels[t]
        cost = 0
        stack = [(root, None)]
        while stack:
            v, pstate = stack.pop()
            if pstate is not None and pstate != state[v]:
                cost += 1
            for w in children[v]:
                stack.append((w, state[v]))
        if best is None or cost < best:
            best = cost
            valid_roots = {state[root]}
        elif cost == best:
            valid_roots.add(state[root])
    return best, valid_roots


def test_fitch_matches_bruteforce():
    task = ParsimonyAncestralStateInference()
    for _ in range(150):
        ex = task.generate_example()
        md = ex.metadata
        children = {int(k): v for k, v in md["children"].items()}
        root = md["root"]
        tip_to_label = {t: md["tip_labels"][t] for t in range(md["n_tips"])}
        sets, cost = _fitch_upward(root, children, tip_to_label)
        bcost, broots = _bruteforce(
            md["tip_labels"], children, root, md["n_tips"], md["n_states"]
        )
        assert cost == bcost
        assert set(sets[root]) == broots


def test_generate_and_validate(task):
    ex = task.generate_example()
    assert ex.metadata is not None
    assert isinstance(ex.answer, str)


def test_score_gold(task):
    for _ in range(60):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_garbage(task):
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer("", ex) != 1.0
        assert task.score_answer("zzz", ex) != 1.0


def test_level_changes_config(task):
    l0 = task.config.__class__()
    l0.set_level(0)
    l6 = task.config.__class__()
    l6.set_level(6)
    assert l0.n_states != l6.n_states or l0.n_tips != l6.n_tips


def test_answer_domains(task):
    letters = set("ABCD")
    for _ in range(60):
        ex = task.generate_example()
        mode = ex.metadata["mode"]
        if mode == 0:
            assert int(ex.answer) >= 1
        else:
            parts = ex.answer.split(",")
            assert all(set(p) <= letters and p for p in parts)
