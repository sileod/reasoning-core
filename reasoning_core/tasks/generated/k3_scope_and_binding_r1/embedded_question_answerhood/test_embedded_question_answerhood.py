import random

import pytest

from reasoning_core.template import Entry

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.embedded_question_answerhood.embedded_question_answerhood import (
    EmbeddedQuestionAnswerhood,
    EmbeddedQuestionConfig,
)


def _make_task(level=0):
    random.seed(3020341981)
    task = EmbeddedQuestionAnswerhood()
    task.config.set_level(level)
    return task


def test_generate_and_score_gold():
    task = _make_task()
    ex = task.generate_example()
    assert isinstance(ex, Entry)
    assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_matches_metadata_verdicts():
    task = _make_task()
    for _ in range(25):
        ex = task.generate_example()
        n = len(ex.metadata["ascriptions"])
        assert len(ex.metadata["verdicts"]) == n
        assert ex.answer == " ".join(ex.metadata["verdicts"])


def test_junk_and_empty_score_zero():
    task = _make_task()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("xyzzy", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0


def test_wrong_verdict_order_scores_zero():
    task = _make_task()
    ex = task.generate_example()
    vals = ex.metadata["verdicts"]
    if len(vals) > 1:
        flipped = list(vals)
        flipped[0], flipped[-1] = flipped[-1], flipped[0]
        if flipped != vals:
            assert task.score_answer(" ".join(flipped), ex) == 0.0


def test_all_labels_appear():
    task = _make_task()
    seen = set()
    for _ in range(120):
        ex = task.generate_example()
        seen.update(ex.metadata["verdicts"])
    assert {"exhaustive", "mention-some", "pair-list"} <= seen


def test_difficulty_scales_count():
    t0 = EmbeddedQuestionAnswerhood()
    t6 = EmbeddedQuestionAnswerhood()
    t0.config.set_level(0)
    t6.config.set_level(6)
    assert t6.config.count > t0.config.count
    assert t0.config.count == 1


def test_known_registered():
    assert EmbeddedQuestionAnswerhood.task_name == "embedded_question_answerhood"


def test_summary_is_single_line():
    s = EmbeddedQuestionAnswerhood.summary
    assert isinstance(s, str) and "\n" not in s and s.strip() == s


def test_design_choice_verbatim():
    dc = EmbeddedQuestionAnswerhood.design_choice
    assert "verdict-only" in dc
    assert "'exhaustive'" in dc and "'mention-some'" in dc and "'pair-list'" in dc
