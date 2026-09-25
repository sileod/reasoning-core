import random

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.permutation_interval_inflation.permutation_interval_inflation import (
    PermutationIntervalInflation as P,
    IntervalInflationConfig,
)


def _examples(task, n):
    return [task.generate_example() for _ in range(n)]


def test_gold_scores_one():
    t = P()
    random.seed(1)
    for x in _examples(t, 20):
        assert t.score_answer(x.answer, x) == 1.0


def test_wrong_and_garbage_score_below_one():
    t = P()
    random.seed(2)
    for x in _examples(t, 20):
        assert t.score_answer("", x) == 0.0
        assert t.score_answer("   ", x) == 0.0
        assert t.score_answer("garbage here", x) == 0.0
        # a wrong permutation
        vals = [int(v) for v in x.answer.split(",")]
        wrong = list(reversed(vals))
        assert t.score_answer(",".join(str(v) for v in wrong), x) == 0.0


def test_answer_is_permutation_of_1_to_total():
    t = P()
    random.seed(3)
    for x in _examples(t, 30):
        total = x.metadata["total"]
        vals = [int(v) for v in x.answer.split(",")]
        assert sorted(vals) == list(range(1, total + 1))


def test_difficulty_changes_config():
    t = P()
    c0 = P.config_cls()
    c0.set_level(0)
    c6 = P.config_cls()
    c6.set_level(6)
    assert c6.total > c0.total


def test_nested_block_present_at_high_levels():
    t = P()
    t.config.set_level(5)
    random.seed(4)
    seen_nested = False
    for x in _examples(t, 20):
        if x.metadata["expr"].startswith("("):
            seen_nested = True
    assert seen_nested


def test_render_and_reparse_match_answer():
    # The stored answer must equal re-expanding the rendered expression.
    from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.permutation_interval_inflation import permutation_interval_inflation as mod

    t = P()
    random.seed(5)
    for x in _examples(t, 20):
        parsed = mod._flatten_expr(x.metadata["expr"])
        assert ",".join(str(v) for v in parsed.expand()) == x.answer
