import random

from reasoning_core.tasks.generated.manual_high_value_80_r1.hindley_milner_inference.hindley_milner_inference import (
    HindleyMilnerInference,
    HindleyMilnerConfig,
    _parse,
    Unifier,
)


def _make(level, seed=0):
    random.seed(seed)
    t = HindleyMilnerInference()
    cfg = HindleyMilnerConfig()
    cfg.apply_difficulty(level)
    t.config = cfg
    return t


def test_gold_scores_1_at_levels():
    for level in [0, 2, 5]:
        for seed in range(5):
            t = _make(level, seed)
            e = t.generate_entry()
            assert t.score_answer(e.answer, e) == 1.0, (level, seed, e.answer)


def test_junk_and_empty_score_0():
    for level in [0, 2, 5]:
        for seed in range(3):
            t = _make(level, seed)
            e = t.generate_entry()
            assert t.score_answer("", e) == 0.0
            assert t.score_answer("garbage", e) == 0.0


def test_parse_free_vars_match_signature():
    for level in [0, 2, 5]:
        for seed in range(5):
            t = _make(level, seed)
            e = t.generate_entry()
            tree, fv = _parse(e.metadata["expr"])
            assert set(fv) == set(e.metadata["signature"].keys())


def test_answer_format_contains_arrow():
    found = False
    for seed in range(30):
        t = _make(5, seed)
        e = t.generate_entry()
        if "->" in e.answer:
            found = True
            break
    assert found


def test_distinct_answers():
    seen = set()
    for seed in range(30):
        t = _make(5, seed)
        e = t.generate_entry()
        seen.add(e.answer)
    assert len(seen) >= 5
