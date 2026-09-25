import random

from reasoning_core.tasks.generated.ua_inference_modes_r4.signed_symmetry_forcing.signed_symmetry_forcing import (
    SignedSymmetryForcing,
    _deduce,
)


def _answers(task, n):
    return [task.generate_example().answer for _ in range(n)]


def test_gold_answer_scores_one():
    random.seed(1)
    task = SignedSymmetryForcing()
    for _ in range(40):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_and_other_answers_score_zero():
    random.seed(2)
    task = SignedSymmetryForcing()
    seen = set()
    for _ in range(40):
        entry = task.generate_example()
        for bad in ("", "yes", "+2", "-2", "1.0", "forced"):
            assert task.score_answer(bad, entry) == 0.0
        for other in seen - {entry.answer}:
            assert task.score_answer(other, entry) == 0.0
        seen.add(entry.answer)


def test_all_three_answer_classes_appear_across_levels():
    random.seed(3)
    task = SignedSymmetryForcing()
    for level in (0, 2, 5):
        task.config.set_level(level)
        seen = set(_answers(task, 120))
        assert seen == {"+1", "-1", "0"}, (level, seen)


def test_deduce_matches_annotated_metadata():
    random.seed(4)
    task = SignedSymmetryForcing()
    for _ in range(60):
        entry = task.generate_example()
        computed = _deduce(
            entry.metadata["relations"],
            entry.metadata["target_start"],
            entry.metadata["target_end"],
        )
        assert computed == entry.answer


def test_no_answer_readable_off_prompt_surface():
    random.seed(5)
    task = SignedSymmetryForcing()
    bad = 0
    for _ in range(80):
        entry = task.generate_example()
        prompt = entry.prompt
        if entry.answer in prompt.split()[-4:]:
            bad += 1
    assert bad == 0


def test_balanced_labels_at_every_level():
    random.seed(6)
    task = SignedSymmetryForcing()
    for level in (0, 3, 6):
        task.config.set_level(level)
        counts = dict.fromkeys(("+1", "-1", "0"), 0)
        for answer in _answers(task, 90):
            counts[answer] += 1
        assert max(counts.values()) <= 50, (level, counts)
