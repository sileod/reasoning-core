import random

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r4.focus_particle_equivalence.focus_particle_equivalence import (
    FocusParticleEquivalence,
)


def test_gold_scores_one_across_levels():
    for level in range(7):
        t = FocusParticleEquivalence()
        t.config.set_level(level)
        for _ in range(30):
            e = t.generate_example(level=level)
            assert t.score_answer(e.answer, e) == 1.0


def test_junk_and_empty_score_zero():
    t = FocusParticleEquivalence()
    e = t.generate_example()
    assert t.score_answer("", e) == 0.0
    assert t.score_answer(None, e) == 0.0
    assert t.score_answer("banana", e) == 0.0
    assert t.score_answer("999", e) == 0.0


def test_reference_always_in_answer():
    t = FocusParticleEquivalence()
    for _ in range(50):
        e = t.generate_example()
        idxs = set(int(x) for x in e.answer.split(","))
        assert 1 in idxs
        assert all(1 <= i <= 5 for i in idxs)


def test_answer_derived_from_semantics():
    from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r4.focus_particle_equivalence.focus_particle_equivalence import (
        _semantics,
    )
    t = FocusParticleEquivalence()
    e = t.generate_example()
    # recompute reference semantics from metadata and check answer consistency
    ref_sem = e.metadata["semantics"][0]
    gold = {i for i, s in enumerate(e.metadata["semantics"], 1) if s == ref_sem}
    assert gold == set(int(x) for x in e.answer.split(","))


def test_difficulty_changes_domain_size():
    t = FocusParticleEquivalence()
    t.config.set_level(0)
    small = t.generate_example().metadata["domain"]
    t.config.set_level(6)
    big = t.generate_example().metadata["domain"]
    assert len(big) >= len(small)


def test_reproducible_under_seed():
    random.seed(2267388306)
    a = FocusParticleEquivalence().generate_example().answer
    random.seed(2267388306)
    b = FocusParticleEquivalence().generate_example().answer
    assert a == b


def test_valid_answers():
    t = FocusParticleEquivalence()
    for _ in range(50):
        e = t.generate_example()
        for x in e.answer.split(","):
            v = int(x)
            assert 1 <= v <= 5
