import random

import pytest

from reasoning_core.template import Entry

from .module import (
    CenteringConfig,
    CenteringTransitionWalk,
    build_utterance,
    render_utterance,
    transition_label,
    utterance_state,
)


def test_generate_example_roundtrip():
    task = CenteringTransitionWalk()
    x = task.generate_example()
    assert isinstance(x.answer, str)
    assert x.answer


def test_gold_scores_one():
    task = CenteringTransitionWalk()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    task = CenteringTransitionWalk()
    x = task.generate_example()
    for junk in ("", " ", "continue", "x y z", 42):
        assert task.score_answer(junk, x) == 0.0


def test_labels_match_expected_token_set():
    task = CenteringTransitionWalk()
    x = task.generate_example()
    allowed = {"establish", "continue", "retain", "smooth-shift", "rough-shift"}
    assert set(x.answer.split()).issubset(allowed)


def test_answer_length_matches_pairs():
    task = CenteringTransitionWalk()
    x = task.generate_example()
    assert len(x.answer.split()) == x.metadata["pairs"]


def test_verifier_internal_consistency():
    for _ in range(50):
        specs = [build_utterance() for _ in range(4)]
        states = [utterance_state(s) for s in specs]
        labels = [transition_label(states[i], states[i + 1]) for i in range(3)]
        st2 = [utterance_state(s) for s in specs]
        lab2 = [transition_label(st2[i], st2[i + 1]) for i in range(3)]
        assert labels == lab2
        for st in states:
            assert st["Cb"] in (None, "A", "B")


def test_all_five_labels_reachable():
    seen = set()
    task = CenteringTransitionWalk()
    for _ in range(4000):
        x = task.generate_example()
        seen.update(x.answer.split())
    assert seen == {"continue", "retain", "smooth-shift", "rough-shift", "establish"}


def test_difficulty_increases_pairs():
    cfg = CenteringConfig()
    cfg.set_level(0)
    l0 = cfg.pairs
    cfg = CenteringConfig()
    cfg.set_level(6)
    l6 = cfg.pairs
    assert l6 > l0


def test_metadata_json_serializable():
    import json

    task = CenteringTransitionWalk()
    x = task.generate_example()
    json.dumps(x.metadata)


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_all_levels_generate(level):
    task = CenteringTransitionWalk()
    task.config.set_level(level)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0
