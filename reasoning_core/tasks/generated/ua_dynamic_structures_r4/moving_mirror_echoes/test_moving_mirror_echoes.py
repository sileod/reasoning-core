import random

from reasoning_core.tasks.generated.ua_dynamic_structures_r4.moving_mirror_echoes.moving_mirror_echoes import (
    MovingMirrorEchoes,
)


def _fresh(level):
    random.seed(12345 + level)
    task = MovingMirrorEchoes()
    task.config.set_level(level)
    return task


def test_generate_and_score():
    random.seed(0)
    task = MovingMirrorEchoes()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_wrong_answers_do_not_score():
    random.seed(1)
    task = MovingMirrorEchoes()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("not a number", x) == 0.0


def test_all_levels_generate():
    for level in range(7):
        random.seed(7 * level)
        task = MovingMirrorEchoes()
        task.config.set_level(level)
        seen = set()
        for _ in range(12):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            seen.add(x.answer)
        assert len(seen) > 1


def test_render_contains_answer_format():
    random.seed(3)
    task = MovingMirrorEchoes()
    x = task.generate_example()
    prompt = task.render_prompt(x.metadata)
    assert "Answer as an integer" in prompt


def test_generation_deterministic_under_seed():
    random.seed(99)
    task = MovingMirrorEchoes()
    task.config.set_level(3)
    a = task.generate_example()
    random.seed(99)
    task2 = MovingMirrorEchoes()
    task2.config.set_level(3)
    b = task2.generate_example()
    assert a.answer == b.answer
    assert a.metadata["speed"] == b.metadata["speed"]


def test_answer_positive_integer_domain():
    random.seed(11)
    task = MovingMirrorEchoes()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(8):
            x = task.generate_example()
            assert int(x.answer) > 0


def test_mirror_state_clean_alternation():
    random.seed(21)
    task = MovingMirrorEchoes()
    task.config.set_level(5)
    x = task.generate_example()
    flags = [False] * len(x.metadata["mirrors"])
    for ev in x.metadata["events"]:
        if ev["kind"] == "activate":
            assert not flags[ev["index"]]
            flags[ev["index"]] = True
        else:
            assert flags[ev["index"]]
            flags[ev["index"]] = False


def test_metadata_json_serializable():
    import json

    random.seed(4)
    task = MovingMirrorEchoes()
    x = task.generate_example()
    json.dumps(dict(x.metadata))
