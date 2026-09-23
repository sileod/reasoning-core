import json
import random

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.reduced_matrix_tour_branching.reduced_matrix_tour_branching import (
    ReducedMatrixTourBranching,
)


def test_generate_and_score():
    t = ReducedMatrixTourBranching()
    for level in (0, 2, 5):
        t.config.set_level(level)
        for _ in range(3):
            ex = t.generate_entry()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_generate_example_roundtrip():
    t = ReducedMatrixTourBranching()
    ex = t.generate_example()
    json.dumps(dict(ex.metadata))
    assert "|" in ex.answer
    num, coords = ex.answer.split("|", 1)
    assert num.isdigit()
    assert coords.count("(") == coords.count(")") and coords.count(",")


def test_wrong_answers_score_zero():
    t = ReducedMatrixTourBranching()
    ex = t.generate_entry()
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("garbage", ex) == 0.0
    assert t.score_answer(ex.answer + ",(9,9)", ex) == 0.0


def test_difficulty_changes():
    t = ReducedMatrixTourBranching()
    t.config.set_level(0)
    s0 = t.config.size
    t.config.set_level(6)
    assert t.config.size > s0


def test_metadata_json_serializable():
    t = ReducedMatrixTourBranching()
    t.config.set_level(5)
    ex = t.generate_entry()
    json.dumps(dict(ex.metadata))


def test_generation_deterministic_under_seed():
    random.seed(1475571465)
    a = ReducedMatrixTourBranching().generate_entry()
    random.seed(1475571465)
    b = ReducedMatrixTourBranching().generate_entry()
    assert a.answer == b.answer


def _bruteforce_opt(matrix, used_cols=frozenset(), row=0):
    n = len(matrix)
    if row == n:
        return 0
    best = None
    for c in range(n):
        if c not in used_cols:
            v = matrix[row][c] + _bruteforce_opt(matrix, used_cols | {c}, row + 1)
            if best is None or v < best:
                best = v
    return best


def test_value_matches_bruteforce():
    t = ReducedMatrixTourBranching()
    t.config.set_level(2)
    for _ in range(5):
        ex = t.generate_entry()
        val = int(ex.answer.split("|", 1)[0])
        assert val == _bruteforce_opt(ex.metadata["matrix"])


def test_answer_has_full_branch_order():
    t = ReducedMatrixTourBranching()
    t.config.set_level(5)
    ex = t.generate_entry()
    coords = ex.answer.split("|", 1)[1]
    n = ex.metadata["size"]
    # every coordinate pair is well-formed and at least one per include branch
    assert coords.count("(") == coords.count(")")
    assert coords.count("(") >= n

