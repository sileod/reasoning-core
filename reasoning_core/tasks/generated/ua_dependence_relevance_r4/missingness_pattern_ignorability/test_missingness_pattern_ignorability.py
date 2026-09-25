import random

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.missingness_pattern_ignorability.missingness_pattern_ignorability import (
    MissingnessPatternIgnorability,
    classify,
)

CLASSES = {"MCAR", "MAR", "MNAR"}


def test_generate_roundtrip():
    task = MissingnessPatternIgnorability()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(30):
            entry = task.generate_example()
            assert entry.answer in CLASSES
            assert task.score_answer(entry.answer, entry) == 1.0


def test_all_classes_each_level():
    task = MissingnessPatternIgnorability()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        seen = set()
        for _ in range(200):
            entry = task.generate_example()
            seen.add(entry.answer)
        assert seen == CLASSES, seen


def test_score_rejects_wrong():
    task = MissingnessPatternIgnorability()
    for _ in range(50):
        entry = task.generate_example()
        for other in CLASSES - {entry.answer}:
            assert task.score_answer(other, entry) == 0.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("   ", entry) == 0.0


def test_classify_consistency():
    assert classify([(0, 0, 0.5), (0, 1, 0.5), (1, 0, 0.5), (1, 1, 0.5)]) == "MCAR"
    assert classify([(0, 0, 0.2), (0, 1, 0.8), (1, 0, 0.2), (1, 1, 0.8)]) == "MAR"
    assert classify([(0, 0, 0.2), (0, 1, 0.8), (1, 0, 0.9), (1, 1, 0.8)]) == "MNAR"
    assert classify([(0, 0, 0.5), (0, 1, 0.5), (1, 0, 0.5), (1, 1, None)]) == "MCAR"


def test_structural_zero_render():
    task = MissingnessPatternIgnorability()
    entry = task.generate_example()
    prompt = task.render_prompt(entry.metadata)
    assert "\u2014" in prompt


def test_generation_distributes_with_zones():
    task = MissingnessPatternIgnorability()
    for level in (0, 6):
        task.config.set_level(level)
        counts = {}
        for _ in range(300):
            entry = task.generate_example()
            counts[entry.answer] = counts.get(entry.answer, 0) + 1
        for c in CLASSES:
            assert counts.get(c, 0) / 300 > 0.15, (level, counts)
