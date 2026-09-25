import random

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.ua_latent_representation_r4.additive_preference_representability import additive_preference_representability as mod

AdditivePreferenceRepresentability = mod.AdditivePreferenceRepresentability
_feasible = mod._feasible


def test_discovery_and_defaults():
    t = AdditivePreferenceRepresentability()
    assert t.config.n_attributes == 5
    assert t.config.n_options == 4


def test_difficulty_changes():
    t = AdditivePreferenceRepresentability()
    base = t.config.n_options
    t.config.set_level(6)
    assert t.config.n_options > base


def test_roundtrip_and_gold_scores():
    t = AdditivePreferenceRepresentability()
    x = t.generate_example()
    assert isinstance(x, Entry)
    assert 1.0 == t.score_answer(x.answer, x)
    assert x.answer in ("infeasible", "feasible_and_forced", "feasible_not_forced")


def test_junk_scores_zero():
    t = AdditivePreferenceRepresentability()
    x = t.generate_example()
    for junk in ("", "42", "yes", "no"):
        assert t.score_answer(junk, x) < 1.0


def test_answers_balanced_over_many():
    t = AdditivePreferenceRepresentability()
    counts = {lbl: 0 for lbl in mod._LABEL_CYCLE}
    for _ in range(30):
        counts[t.generate_example().answer] += 1
    # round-robin keeps every label present and bounded apart
    assert all(v > 0 for v in counts.values()), counts
    assert max(counts.values()) - min(counts.values()) <= 1


def test_reproducible_under_seed_without_shared_state():
    mod._label_count = 0
    random.seed(12345)
    a = AdditivePreferenceRepresentability().generate_example()
    mod._label_count = 0
    random.seed(12345)
    b = AdditivePreferenceRepresentability().generate_example()
    assert a.answer == b.answer
    assert (a.metadata["options"], a.metadata["comparisons"], a.metadata["probe"]) == (
        b.metadata["options"], b.metadata["comparisons"], b.metadata["probe"])


def test_all_levels_generate():
    t = AdditivePreferenceRepresentability()
    for lvl in range(7):
        t.config.set_level(lvl)
        x = t.generate_example()
        assert 1.0 == t.score_answer(x.answer, x)


def test_feasibility_solver_sanity():
    assert _feasible(1, [((1,), (0,))])
    assert _feasible(1, [((1,), (0,)), ((0,), (1,))]) is False
