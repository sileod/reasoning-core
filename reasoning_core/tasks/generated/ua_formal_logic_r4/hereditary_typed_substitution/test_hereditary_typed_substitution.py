from reasoning_core.tasks.generated.ua_formal_logic_r4.hereditary_typed_substitution.hereditary_typed_substitution import (
    HereditaryTypedSubstitution,
)


def test_generate_and_score():
    task = HereditaryTypedSubstitution()
    e = task.generate_example()
    assert task.score_answer(e.answer, e) == 1.0


def test_score_rejects_junk():
    task = HereditaryTypedSubstitution()
    e = task.generate_example()
    assert task.score_answer("banana", e) == 0.0
    assert task.score_answer("", e) == 0.0


def test_difficulty_changes():
    task = HereditaryTypedSubstitution()
    d0 = task.config.depth
    task.config.set_level(6)
    assert task.config.depth > d0


def test_multilevel_gold():
    task = HereditaryTypedSubstitution()
    for level in (0, 1, 2, 3, 4, 5, 6):
        task.config.set_level(level)
        for _ in range(10):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0
            assert task.score_answer("", e) == 0.0
            assert task.score_answer("banana", e) == 0.0


def test_answer_is_balanced():
    task = HereditaryTypedSubstitution()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(10):
            e = task.generate_example()
            s = e.answer
            assert s.count("(") + s.count("<") == s.count(")") + s.count(">")
