import json
import random

import pytest

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.heap_extension_truth.heap_extension_truth import (
    HeapExtensionTruth,
    _all_heaps,
    _parse_truth,
)


@pytest.fixture
def task():
    return HeapExtensionTruth()


def test_gold_scores_one_across_levels(task):
    random.seed(2024)
    for level in range(7):
        counts = {True: 0, False: 0}
        for _ in range(30):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0
            counts[ex.metadata["answer"]] += 1
        assert counts[True] > 0 and counts[False] > 0


def test_metadata_json_roundtrip(task):
    random.seed(7)
    for _ in range(10):
        ex = task.generate_example(level=3)
        dumped = json.dumps(ex.metadata)
        assert dumped
        restored = json.loads(dumped)
        assert restored["formula"]
        assert isinstance(restored["heap"], dict)
        assert isinstance(restored["answer"], bool)


def test_junk_scores_zero(task):
    random.seed(99)
    ex = task.generate_example(level=1)
    for bad in ("", "7", "(0,0)", "Sure", "maybe", "nil", "emp", "false true"):
        assert task.score_answer(bad, ex) == 0.0


def test_parse_truth():
    assert _parse_truth("True") is True
    assert _parse_truth("false") is False
    assert _parse_truth("yes") is True
    assert _parse_truth("  NO ") is False
    assert _parse_truth("1") is True
    assert _parse_truth("0") is False
    assert _parse_truth("maybe") is None
    assert _parse_truth(None) is None
    assert _parse_truth("") is None


def test_levels_0_and_6_headroom(task):
    for level in (0, 6):
        ex = task.generate_example(level=level)
        toks = len(ex.prompt.split())
        assert toks < 2048


def test_all_heaps_single_pointer_per_location():
    heaps = list(_all_heaps(["a", "b"]))
    assert len(heaps) == 16
    for h in heaps:
        assert len(h) <= 2
        assert all(v in ("a", "b", "null") for v in h.values())
