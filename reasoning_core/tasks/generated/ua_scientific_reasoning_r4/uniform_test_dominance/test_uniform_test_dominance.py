import random

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.uniform_test_dominance.uniform_test_dominance import (
    UniformTestDominance,
    UniformTestDominanceConfig,
    _strict_dominates,
    _non_dominated_ids,
    _parse_answer,
    _score_answer,
)


def _make_entry(level, seed):
    task = UniformTestDominance()
    cfg = UniformTestDominanceConfig()
    cfg.set_level(level)
    task.config = cfg
    random.seed(seed)
    return task.generate_entry()


def test_generate_roundtrip_score1():
    random.seed(123)
    task = UniformTestDominance()
    for level in range(7):
        random.seed(1000 + level)
        entry = _make_entry(level, None)
        assert task.score_answer(entry.answer, entry) == 1.0


def test_strict_dominates():
    assert _strict_dominates([0.8, 0.9], [0.7, 0.9]) is True
    assert _strict_dominates([0.7, 0.9], [0.8, 0.9]) is False
    assert _strict_dominates([0.8, 0.9], [0.8, 0.9]) is False
    assert _strict_dominates([0.8, 0.9], [0.8, 0.95]) is False


def test_parse_answer():
    assert _parse_answer("[1, 3]") == [1, 3]
    assert _parse_answer("[]") == []
    assert _parse_answer("") is None
    assert _parse_answer("garbage") is None


def test_score_rejects_junk():
    random.seed(7)
    entry = _make_entry(0, None)
    assert _score_answer("garbage", _parse_answer(entry.metadata["answer"])) == 0.0
    assert _score_answer("", _parse_answer(entry.metadata["answer"])) == 0.0


def test_answer_ids_sorted():
    random.seed(42)
    for i in range(200):
        entry = _make_entry(2, None)
        ids = _parse_answer(entry.metadata["answer"])
        assert ids == sorted(ids)


def test_non_empty_when_valid_rules():
    random.seed(1)
    for level in range(7):
        for _ in range(50):
            entry = _make_entry(level, None)
            valid = [r for r in entry.metadata["rules"] if r["size"] <= entry.metadata["alpha"] + 1e-9]
            if valid:
                assert _parse_answer(entry.metadata["answer"]) != []


def test_answer_varies():
    random.seed(5)
    answers = set()
    for i in range(60):
        entry = _make_entry(3, None)
        answers.add(entry.answer)
    assert len(answers) > 1


def test_dominance_consistency():
    random.seed(9)
    for i in range(100):
        entry = _make_entry(1, None)
        valid = [r for r in entry.metadata["rules"] if r["size"] <= entry.metadata["alpha"] + 1e-9]
        ids = _parse_answer(entry.metadata["answer"])
        assert ids == _non_dominated_ids(valid)
