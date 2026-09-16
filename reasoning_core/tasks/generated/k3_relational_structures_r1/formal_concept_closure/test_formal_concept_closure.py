import random

from reasoning_core.tasks.generated.k3_relational_structures_r1.formal_concept_closure.formal_concept_closure import (
    FormalConceptClosure,
    FormalConceptClosureConfig,
    closure,
    compute_concepts,
    implication_holds,
    intent_of_extent,
    extent_of_intent,
)


def test_prompt_determines_answer():
    t = FormalConceptClosure()
    t.config.mode = "closure"
    e = t.generate_example()
    # re-derive closure from metadata to confirm answer is the true closure
    clos = closure(e.metadata["context"], e.metadata["seed"])
    assert clos == e.metadata["closure"]
    assert t.score_answer(e.answer, e) == 1.0


def test_concepts_gold_is_correct():
    t = FormalConceptClosure()
    t.config.mode = "concepts"
    e = t.generate_example()
    concepts = compute_concepts(e.metadata["context"])
    assert concepts == sorted(tuple(tuple(x) for x in pair) for pair in e.metadata["answer_concepts"])
    assert t.score_answer(e.answer, e) == 1.0


def test_implication_gold_matches_definition():
    t = FormalConceptClosure()
    t.config.mode = "implication"
    e = t.generate_example()
    holds = implication_holds(e.metadata["context"], e.metadata["lhs"], e.metadata["rhs"])
    assert holds == e.metadata["holds"]
    expected = "yes" if holds else "no"
    assert e.answer == expected
    assert t.score_answer(e.answer, e) == 1.0


def test_all_modes_constructible_every_level():
    for mode in ("closure", "concepts", "implication"):
        for level in (0, 2, 5, 6):
            t = FormalConceptClosure()
            cfg = FormalConceptClosureConfig(mode=mode)
            cfg.set_level(level)
            t.config = cfg
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0


def test_junk_and_empty_score_zero():
    t = FormalConceptClosure()
    for mode in ("closure", "concepts", "implication"):
        cfg = FormalConceptClosureConfig(mode=mode)
        cfg.set_level(0)
        t.config = cfg
        e = t.generate_example()
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("garbage", e) == 0.0
        assert t.score_answer("0", e) == 0.0


def test_implication_answer_balanced():
    t = FormalConceptClosure()
    cfg = FormalConceptClosureConfig(mode="implication")
    cfg.set_level(0)
    t.config = cfg
    counts = {"yes": 0, "no": 0}
    for _ in range(80):
        e = t.generate_example()
        counts[e.answer] += 1
    assert counts["yes"] >= 5 and counts["no"] >= 5


def test_concepts_dedup_key_stable():
    t = FormalConceptClosure()
    t.config.mode = "closure"
    a = t.generate_example()
    b = t.generate_example()
    assert a.deduplication_key is not None
