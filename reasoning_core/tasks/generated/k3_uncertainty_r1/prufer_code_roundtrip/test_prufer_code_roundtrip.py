import random

from reasoning_core.tasks.generated.k3_uncertainty_r1.prufer_code_roundtrip.prufer_code_roundtrip import (
    PruferCodeRoundtrip,
    rooted_parent,
    tree_to_prufer,
)


def test_roundtrip_all_levels():
    task = PruferCodeRoundtrip()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_rooted_parent():
    edges = [(1, 2), (2, 3), (3, 4)]
    parent = rooted_parent(edges, 4, root=1)
    assert parent[2] == 1
    assert parent[3] == 2
    assert parent[4] == 3


def test_tree_to_prufer_small():
    edges = [(1, 2), (2, 3), (3, 4)]
    code = tree_to_prufer(edges, 4)
    assert code == [2, 3]


def test_score_junk():
    task = PruferCodeRoundtrip()
    x = task.generate_example()
    assert task.score_answer("", x) < 1.0
    assert task.score_answer("junk", x) < 1.0
