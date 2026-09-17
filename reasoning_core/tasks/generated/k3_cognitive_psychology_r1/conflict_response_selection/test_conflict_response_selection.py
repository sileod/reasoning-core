import collections

import pytest

from reasoning_core.tasks.generated.k3_cognitive_psychology_r1.conflict_response_selection.conflict_response_selection import (
    ConflictResponseSelection,
    displayed_dimensions,
    response,
    verified_answer,
)

LABELS = ("LEFT", "RIGHT", "CONGRUENT", "INCONGRUENT")


def _counts(level):
    task = ConflictResponseSelection()
    task.config.set_level(level)
    answers = collections.Counter()
    for _ in range(400):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0
        assert verified_answer(e.metadata) == e.answer
        answers[e.answer] += 1
    return answers


def test_levels_generate_and_score():
    for level in range(7):
        c = _counts(level)
        assert len(c) >= 2, (level, c)


def test_labels_balanced():
    c = _counts(3)
    total = sum(c.values())
    for label, n in c.items():
        assert n / total > 0.15, (label, c)


def test_wrong_answer_scores_zero():
    task = ConflictResponseSelection()
    for _ in range(50):
        e = task.generate_example()
        for wrong in LABELS:
            if wrong != e.answer:
                assert task.score_answer(wrong, e) == 0.0
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("banana", e) == 0.0
        assert task.score_answer(None, e) == 0.0


def test_response_chains_through_all_stages():
    task = ConflictResponseSelection()
    task.config.set_level(4)
    for _ in range(100):
        m = task.generate_example().metadata
        target, _ = displayed_dimensions(m)
        value = target
        for table in m["tables"]:
            value = table[value]
        assert m["keys"][value] == response(target, m)
        assert response(target, m) in ("LEFT", "RIGHT")


def test_verdict_and_response_semantics():
    task = ConflictResponseSelection()
    task.config.set_level(2)
    for _ in range(100):
        m = task.generate_example().metadata
        target, distractor = displayed_dimensions(m)
        target_key = response(target, m)
        distractor_key = distractor if m["family"] == "simon" else response(distractor, m)
        congruent = target_key == distractor_key
        if m["mode"] == "verdict":
            assert verified_answer(m) == ("CONGRUENT" if congruent else "INCONGRUENT")
        else:
            assert verified_answer(m) == target_key


def test_config_difficulty_changes():
    base = ConflictResponseSelection.config_cls()
    base.set_level(6)
    assert base.stages > 1


def test_prompt_and_answer_match_mode():
    task = ConflictResponseSelection()
    for _ in range(50):
        e = task.generate_example()
        p = task.render_prompt(e.metadata)
        assert e.answer in LABELS
        assert ("CONGRUENT" in p) == (e.metadata["mode"] == "verdict")
