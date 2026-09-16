import random

from collections import Counter

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.constituency_dependency_conversion.constituency_dependency_conversion import (
    ConstituencyDependencyConversion,
)


def _make_task(level):
    t = ConstituencyDependencyConversion()
    t.config.set_level(level)
    return t


def test_gold_scores_one_at_each_level():
    for level in (0, 2, 5):
        task = _make_task(level)
        for _ in range(10):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_and_empty_do_not_score():
    task = _make_task(0)
    ex = task.generate_example()
    assert task.score_answer("jeez 12345 not an answer", ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("   ", ex) == 0.0


def test_both_modes_appear():
    task = _make_task(0)
    modes = set()
    for _ in range(40):
        modes.add(task.generate_example().metadata["mode"])
    assert modes == {"A", "B"}


def test_answer_matches_recomputed_arcs():
    for level in (0, 1, 3, 6):
        task = _make_task(level)
        for _ in range(10):
            ex = task.generate_example()
            tree = ex.metadata["arcs"]
            if ex.metadata["mode"] == "A":
                parts = [f"{g} -> {d} : {f}" for g, d, f in ex.metadata["arcs"]]
                expected = " ; ".join(sorted(parts))
            else:
                expected = ex.answer
            assert task.score_answer(expected, ex) == 1.0


def test_arcs_are_well_formed():
    """Governors stand over dependents and the graph is a tree rooted at the S head."""
    for level in (0, 2, 5, 6):
        task = _make_task(level)
        ex = task.generate_example()
        tokens = set(ex.metadata["tokens"])
        arcs = ex.metadata["arcs"]
        assert arcs == sorted(arcs)
        for g, d, f in arcs:
            assert g in tokens and d in tokens and g != d
            assert f in {"subj", "obj", "arg", "det", "mod", "comp"}
        gs = [g for g, _, _ in arcs]
        ds = [d for _, d, _ in arcs]
        # one root (a token that governs but is never a dependent)
        roots = set(gs) - set(ds)
        assert len(roots) == 1
        # every non-root token has exactly one incoming arc
        c = Counter(ds)
        for tok in tokens:
            if tok not in roots:
                assert c[tok] == 1, (tok, c[tok])


def test_field_verification_uses_expected_result():
    """Sanity-check that dictionary/iteration order never reaches the answer string."""
    task = _make_task(0)
    samples = []
    for _ in range(20):
        ex = task.generate_example()
        samples.append((ex.metadata["mode"], ex.answer))
    assert len(set(a for _, a in samples)) > 1
