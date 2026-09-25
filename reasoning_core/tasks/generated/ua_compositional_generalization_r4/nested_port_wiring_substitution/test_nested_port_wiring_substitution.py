from reasoning_core.tasks.generated.ua_compositional_generalization_r4.nested_port_wiring_substitution.nested_port_wiring_substitution import NestedPortWiringSubstitution


def test_generate_and_score():
    task = NestedPortWiringSubstitution()
    for level in range(7):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_bad_answers_fail():
    task = NestedPortWiringSubstitution()
    task.config.set_level(2)
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("zzz", x) == 0.0
    assert task.score_answer(None, x) == 0.0


def test_reversed_flag_changes_answer():
    task = NestedPortWiringSubstitution()
    task.config.set_level(2)
    samples = set()
    for _ in range(30):
        samples.add(task.generate_example().answer)
    assert len(samples) > 1


def test_difficulty_changes():
    task = NestedPortWiringSubstitution()
    task.config.set_level(0)
    c0 = task.config.count
    task.config.set_level(6)
    c6 = task.config.count
    assert c6 > c0
