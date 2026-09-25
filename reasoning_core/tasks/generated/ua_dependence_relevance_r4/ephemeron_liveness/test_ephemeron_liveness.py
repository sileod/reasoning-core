import random

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.ephemeron_liveness.ephemeron_liveness import (
    EphemeronLiveness,
    EphemeronLivenessConfig,
    compute_alive,
    label,
    render_answer,
)


def test_generate_example_scores_one():
    t = EphemeronLiveness()
    for _ in range(20):
        x = t.generate_example()
        assert t.score_answer(x.answer, x) == 1
        assert isinstance(x.answer, str)


def test_answer_matches_fixpoint():
    t = EphemeronLiveness()
    for _ in range(20):
        x = t.generate_example()
        m = x.metadata
        alive = compute_alive(m["n"], m["roots"], [tuple(e) for e in m["strong"]],
                              [tuple(e) for e in m["weak"]],
                              [tuple(e) for e in m["ephems"]])
        assert x.answer == render_answer(alive, m["n"])


def test_weak_edge_never_retains():
    # A single strong root and one object only weakly referenced: that object dies.
    n = 2
    roots = [0]
    strong = []
    weak = [(0, 1)]
    ephems = []
    alive = compute_alive(n, roots, strong, weak, ephems)
    assert 1 not in alive
    assert alive == {0}
    assert render_answer(alive, n) == label(0)


def test_strong_edge_retains():
    n = 2
    roots = [0]
    strong = [(0, 1)]
    alive = compute_alive(n, roots, strong, weak=[], ephems=[])
    assert alive == {0, 1}
    assert render_answer(alive, n) == "AB"


def test_ephemeron_needs_container_and_key():
    # Value dies when the key is alive but the container is not.
    n = 3
    roots = [1]
    strong = []
    ephems = [(0, 1, 2)]  # container 0 dead, key 1 alive -> value 2 dead
    alive = compute_alive(n, roots, strong, weak=[], ephems=ephems)
    assert alive == {1}
    # Value dies when the key is dead but the container is alive.
    n2 = 3
    roots2 = [0]
    ephems2 = [(0, 1, 2)]  # container 0 alive, key 1 dead -> value 2 dead
    alive2 = compute_alive(n2, roots2, strong, weak=[], ephems=ephems2)
    assert alive2 == {0}
    # Both alive -> value survives.
    n3 = 3
    roots3 = [0]
    strong3 = [(0, 1)]
    ephems3 = [(0, 1, 2)]  # container and key both alive -> value survives
    alive3 = compute_alive(n3, roots3, strong3, weak=[], ephems=ephems3)
    assert alive3 == {0, 1, 2}


def test_chained_ephemeron_activation():
    # value 2 is the key for an ephemeron retaining value 3.
    n = 4
    roots = [0]
    strong = [(0, 1)]
    ephems = [(1, 1, 2), (1, 2, 3)]  # then 2 stays alive via first, activating second
    alive = compute_alive(n, roots, strong, weak=[], ephems=ephems)
    assert alive == {0, 1, 2, 3}


def test_difficulty_changes(): 
    t = EphemeronLiveness()
    c0 = EphemeronLivenessConfig()
    c0.set_level(0)
    c6 = EphemeronLivenessConfig()
    c6.set_level(6)
    assert c0.n < c6.n


def test_answers_vary():
    t = EphemeronLiveness()
    answers = {t.generate_example().answer for _ in range(60)}
    assert len(answers) > 1


def test_gold_applyback_consistency():
    random.seed(1234)
    t = EphemeronLiveness()
    for _ in range(30):
        x = t.generate_example()
        m = x.metadata
        recomputed = create_object_labels(m)
        assert set(recomputed) == {label(i) for i in m["alive"]}


def create_object_labels(m):
    alive = compute_alive(m["n"], m["roots"], [tuple(e) for e in m["strong"]],
                          [tuple(e) for e in m["weak"]],
                          [tuple(e) for e in m["ephems"]])
    return [label(i) for i in alive]
