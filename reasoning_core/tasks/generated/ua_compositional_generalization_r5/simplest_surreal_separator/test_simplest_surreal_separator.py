import random

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.simplest_surreal_separator.simplest_surreal_separator import (
    SimplestSurrealSeparator,
    _earliest_between,
    _render_surreal,
)


def test_earliest_between_basic():
    assert _earliest_between(0, 1) == 0.5
    assert _earliest_between(0, 0.5) == 0.25


def test_earliest_between_negative():
    assert _earliest_between(-2, -1) == -1.5


def test_earliest_between_invalid():
    assert _earliest_between(3, 2) is None
    assert _earliest_between(1, 1) is None


def test_render_surreal():
    assert _render_surreal(0.75) == "3/4"
    assert _render_surreal(-0.5) == "-1/2"
    assert _render_surreal(3) == "3"


def test_task_generates():
    random.seed(3867019559)
    task = SimplestSurrealSeparator()
    for level in (0, 3, 6):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_domain():
    random.seed(3867019559)
    task = SimplestSurrealSeparator()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(50):
            entry = task.generate_example()
            if entry.answer == "invalid":
                continue
            parts = entry.answer.split("/")
            if len(parts) == 1:
                pass
            else:
                n, d = int(parts[0]), int(parts[1])
                assert abs(n) < d or abs(n) % d != 0


def test_invalid_only_when_left_ge_right():
    random.seed(3867019559)
    task = SimplestSurrealSeparator()
    for level in (0, 2, 5):
        task.config.set_level(level)
        found_invalid = False
        found_valid = False
        for _ in range(300):
            entry = task.generate_example()
            left = int(entry.metadata["left"].split("/")[0]) / (
                int(entry.metadata["left"].split("/")[1]) if "/" in entry.metadata["left"] else 1
            )
            right = int(entry.metadata["right"].split("/")[0]) / (
                int(entry.metadata["right"].split("/")[1]) if "/" in entry.metadata["right"] else 1
            )
            if entry.answer == "invalid":
                found_invalid = True
                assert left >= right
            else:
                found_valid = True
                assert left < right
        assert found_invalid and found_valid
