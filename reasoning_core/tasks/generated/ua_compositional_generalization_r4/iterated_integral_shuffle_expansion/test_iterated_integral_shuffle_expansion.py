from reasoning_core.tasks.generated.ua_compositional_generalization_r4.iterated_integral_shuffle_expansion import (
    iterated_integral_shuffle_expansion as mod,
)
from reasoning_core.tasks.generated.ua_compositional_generalization_r4.iterated_integral_shuffle_expansion.iterated_integral_shuffle_expansion import (
    IteratedIntegralShuffleExpansion,
)


def test_gold_scores_one():
    task = IteratedIntegralShuffleExpansion()
    for _ in range(30):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_expand_simple():
    c = mod.expand_product([("a", "b"), ("c",)])
    assert mod.canonical_answer(c) == "abc + acb + cab"


def test_multiplicity_collected():
    c = mod.expand_product([("a",), ("a",)])
    assert c == {("a", "a"): 2}
    assert mod.canonical_answer(c) == "2*aa"


def test_score_rejects_junk_empty():
    task = IteratedIntegralShuffleExpansion()
    e = task.generate_example()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("zzz not a real answer", e) == 0.0


def test_difficulty_changes_config():
    task = IteratedIntegralShuffleExpansion()
    base = task.config.max_len
    task.config.set_level(5)
    assert task.config.n_factors == 3
    assert task.config.max_len >= base


def test_parse_roundtrip():
    c = mod.expand_product([("a", "b"), ("b",), ("c", "a")])
    ans = mod.canonical_answer(c)
    assert mod.parse_answer(ans) == c
