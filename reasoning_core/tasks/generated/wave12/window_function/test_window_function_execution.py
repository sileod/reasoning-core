from reasoning_core.tasks.generated.wave12.window_function_execution.window_function_execution import (
    WindowFunctionV3,
)


def test_gold_scores_one():
    t = WindowFunctionV3()
    for _ in range(200):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_balanced_labels():
    t = WindowFunctionV3()
    yes = 0
    no = 0
    for _ in range(300):
        e = t.generate_example()
        if e.answer == "yes":
            yes += 1
        else:
            no += 1
    assert yes > 60 and no > 60


def test_garbage_scores_zero():
    t = WindowFunctionV3()
    for _ in range(100):
        e = t.generate_example()
        assert t.score_answer("maybe", e) == 0.0
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("42", e) == 0.0
        assert t.score_answer("yes", e) == (1.0 if e.answer == "yes" else 0.0)
        assert t.score_answer("no", e) == (1.0 if e.answer == "no" else 0.0)
        assert t.score_answer(" YES ", e) == (1.0 if e.answer == "yes" else 0.0)


def test_gold_is_recomputable():
    from reasoning_core.tasks.generated.wave12.window_function_execution.window_function_execution import (
        compute_answer,
    )

    t = WindowFunctionV3()
    for _ in range(200):
        e = t.generate_example()
        gold = compute_answer(e.metadata)
        shown = e.metadata["target_val"]
        expect_yes = (shown is None) or (shown == gold)
        assert e.answer == ("yes" if expect_yes else "no")
