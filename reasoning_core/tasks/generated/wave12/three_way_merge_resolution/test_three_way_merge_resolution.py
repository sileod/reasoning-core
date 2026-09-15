import random

from reasoning_core.tasks.generated.wave12.three_way_merge_resolution.three_way_merge_resolution import (
    ThreeWayMergeResolution,
)


def test_generate_and_score():
    random.seed(1602009423)
    task = ThreeWayMergeResolution()
    for _ in range(200):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0
        assert task.score_answer("", e) < 1.0
        assert task.score_answer("junk", e) < 1.0


def test_constant_answer_not_always_same():
    random.seed(1234)
    task = ThreeWayMergeResolution()
    answers = set()
    for _ in range(100):
        answers.add(task.generate_example().answer)
    assert len(answers) > 5


def test_prompt_determines_answer():
    random.seed(99)
    task = ThreeWayMergeResolution()
    e = task.generate_example()
    prompt = task.render_prompt(e.metadata)
    # re-rendering the same metadata gives identical prompt -> same answer
    assert task.render_prompt(e.metadata) == prompt


def test_conflicts_present_and_absent():
    random.seed(2024)
    task = ThreeWayMergeResolution()
    saw_conflict = saw_plain = False
    for _ in range(300):
        e = task.generate_example()
        if "<" in e.answer:
            saw_conflict = True
        else:
            saw_plain = True
    assert saw_conflict and saw_plain


def test_all_levels_generate():
    random.seed(7)
    for level in range(0, 7):
        task = ThreeWayMergeResolution()
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0

