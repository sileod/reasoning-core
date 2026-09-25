import random

from reasoning_core.tasks.generated.ua_invariants_r4.frame_independent_observables.frame_independent_observables import (
    FrameIndependentObservables,
)


def test_gold_scores_one():
    random.seed(7)
    task = FrameIndependentObservables()
    for _ in range(64):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_render_round_trip():
    random.seed(3)
    task = FrameIndependentObservables()
    for _ in range(32):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        assert "O = " in prompt and "yes" in prompt and "no" in prompt
        assert prompt.endswith("single word.")


def test_wrong_and_junk():
    random.seed(11)
    task = FrameIndependentObservables()
    for _ in range(64):
        ex = task.generate_example()
        junk = ["", "   ", "42", "maybe", "yesplease", "nope", "certainly", "answer"]
        for j in junk:
            assert task.score_answer(j, ex) < 1.0
        other = "no" if ex.answer == "yes" else "yes"
        assert task.score_answer(other, ex) == 0.0


def test_answer_domain():
    random.seed(5)
    task = FrameIndependentObservables()
    for _ in range(200):
        ex = task.generate_example()
        assert ex.answer in ("yes", "no")


def test_levels_generate():
    random.seed(13)
    for level in range(7):
        task = FrameIndependentObservables()
        task.config.set_level(level)
        for _ in range(8):
            ex = task.generate_example()
            assert ex.answer in ("yes", "no")

        labels = set()
        for _ in range(40):
            labels.add(task.generate_example().answer)
        assert labels == {"yes", "no"}, f"level {level} not balanced in labels"
