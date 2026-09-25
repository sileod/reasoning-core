from reasoning_core.tasks.generated.ua_compositional_generalization_r4.hysteresis_reversal_memory.hysteresis_reversal_memory import (
    HysteresisReversalMemory,
)


def test_gold_scores():
    task = HysteresisReversalMemory()
    for _ in range(200):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0
        assert task.score_answer("", e) < 1.0
        assert task.score_answer("junk!!", e) < 1.0


def test_levels_generate():
    task = HysteresisReversalMemory()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0


def test_answer_domain():
    task = HysteresisReversalMemory()
    for _ in range(100):
        e = task.generate_example()
        md = e.metadata
        if md["mode"] == "branch":
            assert e.answer in (str(md["low"]), str(md["high"]))
        else:
            if e.answer == "none":
                assert md["answer_list"] == []
            else:
                terms = [int(x) for x in e.answer.split(", ")]
                assert all(md["low"] <= t <= md["high"] for t in terms)
