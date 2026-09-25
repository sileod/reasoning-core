from reasoning_core.tasks.generated.ua_language_implementation_r4.attentional_blink_gating.attentional_blink_gating import (
    AttentionalBlinkGating,
)


def test_generate_and_score():
    task = AttentionalBlinkGating()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_multiple_answers_exist():
    task = AttentionalBlinkGating()
    answers = set()
    for _ in range(200):
        ex = task.generate_example()
        answers.add(ex.answer)
    assert len(answers) > 1


def test_metadata_json_serializable():
    import json

    task = AttentionalBlinkGating()
    for level in (0, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        json.dumps(ex.metadata)


def test_prompt_includes_givens():
    task = AttentionalBlinkGating()
    task.config.set_level(0)
    ex = task.generate_example()
    prompt = task.render_prompt(ex.metadata)
    assert "recovery" in prompt
    assert "admitted" in prompt
