import random
from reasoning_core.tasks.generated.k3_semantics_preserving_translation_r1.simplicial_boundary_matrices.simplicial_boundary_matrices import (
    SimplicialBoundaryMatrices, SimplicialConfig, _sparse_string,
)


def test_domain_gf2():
    random.seed(1)
    t = SimplicialBoundaryMatrices()
    t.config.max_verts = 6
    t.config.mode = "gf2"
    ex = t.generate_example()
    assert t.score_answer(ex.answer, ex) == 1.0
    assert _sparse_string(True, 0, 0, {}) == "0x0x0"


def test_domain_signed():
    random.seed(2)
    t = SimplicialBoundaryMatrices()
    t.config.mode = "signed"
    ex = t.generate_example()
    assert t.score_answer(ex.answer, ex) == 1.0


def test_domain_reverse():
    random.seed(3)
    t = SimplicialBoundaryMatrices()
    t.config.mode = "reverse"
    ex = t.generate_example()
    assert t.score_answer(ex.answer, ex) == 1.0
    nverts = ex.metadata["nverts"]
    for f in ex.answer.split(";"):
        for x in f.split(","):
            assert x != ""
            assert 0 <= int(x) < nverts


def test_wrong_answer_scored_zero():
    random.seed(4)
    t = SimplicialBoundaryMatrices()
    exs = [t.generate_example() for _ in range(20)]
    for ex in exs:
        assert t.score_answer("junk", ex) == 0.0


def test_exact_match_requires_same():
    t = SimplicialBoundaryMatrices()
    ex = type("E", (), {"answer": "1,0:1"})()
    assert t.score_answer("1,0:1", ex) == 1.0
    assert t.score_answer("1,0:1;", ex) == 0.0
    assert t.score_answer("1,0:1 ;2,0:1", ex) == 0.0
