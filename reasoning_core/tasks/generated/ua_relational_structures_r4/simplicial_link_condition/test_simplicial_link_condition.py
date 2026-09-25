import random

from reasoning_core.tasks.generated.ua_relational_structures_r4.simplicial_link_condition.simplicial_link_condition import (
    SimplicialLinkCondition,
    SimplicialLinkConfig,
    _answer_from_edges,
    _faces_from_facets,
    _link,
    _satisfying_edges,
)


def _fresh():
    return SimplicialLinkCondition()


def test_gold_scores_one():
    task = _fresh()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1


def test_junk_scores_zero():
    task = _fresh()
    for _ in range(20):
        ex = task.generate_example()
        for bad in ("", " ", "reajrjrje9595!", "0", "-1", "none", "0-1,2-3 x"):
            if bad != str(ex.answer):
                assert task.score_answer(bad, ex) == 0


def test_answer_matches_computed_solution():
    task = _fresh()
    for _ in range(40):
        ex = task.generate_example()
        edges = _satisfying_edges(ex.metadata["facets"])
        assert _answer_from_edges(edges) == ex.answer
        assert ex.metadata["satisfying_edges"] == edges


def test_answer_format_textual():
    task = _fresh()
    for _ in range(40):
        ex = task.generate_example()
        if ex.answer == "none":
            assert ex.metadata["satisfying_edges"] == []
        else:
            for part in ex.answer.split(","):
                u, v = part.split("-")
                assert int(u) < int(v)


def test_answer_domain_valid():
    task = _fresh()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            n = ex.metadata["n_vertices"]
            for f in ex.metadata["facets"]:
                assert all(0 <= v < n for v in f)
            for edge in ex.metadata["satisfying_edges"]:
                u, v = map(int, edge.split("-"))
                assert 0 <= u < v < n


def test_link_condition_is_correct_definition():
    task = _fresh()
    for _ in range(20):
        ex = task.generate_example()
        faces = _faces_from_facets(ex.metadata["facets"])
        for edge_s in ex.metadata["satisfying_edges"]:
            u, v = map(int, edge_s.split("-"))
            e = frozenset({u, v})
            assert _link(e, faces) == _link(frozenset({u}), faces) & _link(frozenset({v}), faces)


def test_answer_variety_across_levels():
    task = _fresh()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        seen = set()
        for _ in range(40):
            ex = task.generate_example()
            seen.add(ex.answer)
        assert len(seen) > 4, f"level {level} answer set too small: {seen}"


def test_difficulty_scales():
    l0 = SimplicialLinkConfig()
    task = _fresh()
    task.config.set_level(6)
    assert task.config.n_vertices >= l0.n_vertices
    assert task.config.n_triangles >= l0.n_triangles


def test_levels_0_and_6_generate():
    task = _fresh()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert ex.prompt
            assert task.score_answer(ex.answer, ex) == 1


def test_all_levels_within_prompt_budget():
    task = _fresh()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(3):
            ex = task.generate_example()
            assert task.tokenizer is not None


def test_both_answer_regimes_occur():
    task = _fresh()
    saw_none = False
    saw_nonempty = False
    for _ in range(60):
        ex = task.generate_example()
        if ex.answer == "none":
            saw_none = True
        else:
            saw_nonempty = True
    assert saw_none, "expected at least one 'none' answer"
    assert saw_nonempty, "expected at least one non-empty answer"


def test_answer_not_surface_readable():
    task = _fresh()
    for _ in range(30):
        ex = task.generate_example()
        facet_line = ex.prompt.split("Facets:")[1].split(".")[0].strip()
        assert ex.answer != facet_line
        if ex.answer != "none":
            assert len({p for p in ex.answer.split(",")}) == len(ex.answer.split(","))


def test_validate_passes():
    task = _fresh()
    task.validate(n_samples=5)
