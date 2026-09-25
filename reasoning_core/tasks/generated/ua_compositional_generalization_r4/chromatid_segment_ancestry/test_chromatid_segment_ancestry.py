import random

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.chromatid_segment_ancestry import (
    chromatid_segment_ancestry as mod,
)

TASK = mod.ChromatidSegmentAncestry


def _fresh(level=0):
    return TASK(_level=level)


def test_generates_and_scores():
    t = _fresh()
    for level in (0, 2, 5):
        t.config.set_level(level)
        for _ in range(10):
            x = t.generate_example()
            assert t.score_answer(x.answer, x) == 1
            assert len(x.answer) == t.config.n_markers
            assert set(x.answer) <= {"0", "1"}


def test_answer_length_matches_markers():
    t = _fresh()
    for level in (0, 6):
        t.config.set_level(level)
        x = t.generate_example()
        assert len(x.answer) == t.config.n_markers


def test_recompute_matches_metadata_final():
    t = _fresh()
    for level in (0, 2, 5):
        t.config.set_level(level)
        for _ in range(8):
            x = t.generate_example()
            m = x.metadata
            final = mod.apply_events(m["n"], m["events"])
            recomputed = "".join(str(v) for v in final[mod.IDX[m["query"]]])
            assert recomputed == m["final"][m["query"]]
            assert recomputed == x.answer


def test_domain_answer_is_bit_string():
    t = _fresh()
    for level in (0, 6):
        t.config.set_level(level)
        for _ in range(5):
            x = t.generate_example()
            n = t.config.n_markers
            assert len(x.answer) == n
            for ch in x.answer:
                assert ch in ("0", "1")


def test_garbage_not_scored_correct():
    t = _fresh()
    x = t.generate_example()
    assert t.score_answer("", x) < 1
    assert t.score_answer("abcxyz", x) < 1
    assert t.score_answer("10101" * 5, x) < 1


def test_not_constant_answers():
    t = _fresh()
    t.config.set_level(0)
    answers = {t.generate_example().answer for _ in range(20)}
    assert len(answers) > 1


def test_difficulty_changes_config():
    t = _fresh()
    c0 = (t.config.n_markers, t.config.n_events)
    t.config.set_level(6)
    c6 = (t.config.n_markers, t.config.n_events)
    assert c0 != c6
    assert c6[0] > c0[0] and c6[1] > c0[1]


def test_level6_generates_quickly():
    t = _fresh()
    t.config.set_level(6)
    import time
    t0 = time.time()
    x = t.generate_example()
    assert time.time() - t0 < 3
    assert t.score_answer(x.answer, x) == 1


def test_metadata_json_serializable():
    import json
    t = _fresh()
    x = t.generate_example()
    json.dumps(dict(x.metadata))


def test_prompt_mentions_query_and_format():
    t = _fresh()
    x = t.generate_example()
    assert t.render_prompt(x.metadata).count("position") >= 1
