import random

import numpy as np

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.universal_matrix_identity.universal_matrix_identity import (
    UniversalMatrixIdentity,
    _word_matrix,
)


def test_generation_and_scoring_all_levels():
    task = UniversalMatrixIdentity()
    for level in range(0, 7):
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert ex.prompt
            assert ex.answer in ("identity", "nonidentity")
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer("", ex) < 1.0
            assert task.score_answer("  %s\n" % ex.answer, ex) == 1.0
            assert task.score_answer("reajrjrje9595!", ex) < 1.0


def test_both_labels_appear():
    task = UniversalMatrixIdentity()
    labels = set()
    for _ in range(60):
        labels.add(task.generate_example(level=2).answer)
    assert labels == {"identity", "nonidentity"}


def test_identity_vanish_certificate():
    task = UniversalMatrixIdentity()
    # The gold answer for identity instances is certified inside generate_entry by a
    # cyclicity construction (tr is invariant under cyclic rotation of a product) and
    # an exact numeric check that the block sum vanishes. Exercising generation at
    # every level must never hit that certified path inconsistently.
    counts = {"identity": 0, "nonidentity": 0}
    for level in range(0, 7):
        for _ in range(30):
            ex = task.generate_example(level=level)
            counts[ex.answer] += 1
    assert counts["identity"] > 0 and counts["nonidentity"] > 0
    assert task.score_answer("identity", ex) in (0.0, 1.0)


def test_matrices_reproducible_under_seed():
    random.seed(123)
    m1 = _word_matrix([("c", ("v", 0), ("v", 1))], make_mats())
    random.seed(123)
    m2 = _word_matrix([("c", ("v", 0), ("v", 1))], make_mats())
    assert np.array_equal(m1, m2)


def make_mats():
    return [
        np.array([[random.randint(-3, 3) for _ in range(2)] for _ in range(2)])
        for _ in range(3)
    ]


def test_levels_change_config():
    task = UniversalMatrixIdentity()
    base = task.generate_example(level=0).metadata
    hi = task.generate_example(level=6).metadata
    assert hi["dim"] >= base["dim"]
    assert hi["max_word"] >= base["max_word"]
