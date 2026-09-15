import random

from reasoning_core.tasks.generated.k3_rule_induction_r1.repeating_decimal_expansion.repeating_decimal_expansion import (
    RepeatingDecimalExpansion,
    long_division,
    format_expansion,
)


def test_generate_and_score():
    random.seed(0)
    task = RepeatingDecimalExpansion()
    for _ in range(50):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        assert x.metadata["answer"] == x.answer
        assert task.score_answer(x.answer, x) == 1.0
        assert task.score_answer("", x) == 0.0
        assert task.score_answer("garbage", x) == 0.0
        assert len(prompt) > 0


def test_format_matches_long_division():
    random.seed(1)
    task = RepeatingDecimalExpansion()
    for _ in range(50):
        x = task.generate_example()
        sign, ip, pre, rep = long_division(
            x.metadata["numerator"], x.metadata["denominator"]
        )
        expected = format_expansion(sign, ip, pre, rep)
        assert x.metadata["answer"] == expected


def test_difficulty_changes():
    task = RepeatingDecimalExpansion()
    c0 = task.config.__class__(level=0)
    c0.set_level(0)
    c6 = task.config.__class__(level=6)
    c6.set_level(6)
    assert c6.num_max > c0.num_max


def test_all_modes_present():
    random.seed(3)
    task = RepeatingDecimalExpansion()
    modes = set()
    for _ in range(200):
        x = task.generate_example()
        modes.add(x.metadata["mode"])
    assert "terminating" in modes
    assert "pure" in modes
    assert "mixed" in modes


def test_no_surface_leak():
    random.seed(5)
    task = RepeatingDecimalExpansion()
    for _ in range(50):
        x = task.generate_example()
        prompt = task.render_prompt(x.metadata)
        assert x.answer not in prompt


def test_true_recurrence_structure():
    task = RepeatingDecimalExpansion()
    random.seed(7)
    for _ in range(200):
        x = task.generate_example()
        mode = x.metadata["mode"]
        if mode == "terminating":
            assert x.metadata["repetend"] == ""
            assert x.metadata["preperiod"] != "" or x.metadata["integer_part"] != ""
        elif mode == "pure":
            assert x.metadata["preperiod"] == ""
            assert x.metadata["repetend"] != ""
        else:
            assert x.metadata["preperiod"] != ""
            assert x.metadata["repetend"] != ""


def test_answer_is_canonical_string():
    task = RepeatingDecimalExpansion()
    random.seed(11)
    assert task.score_answer("not numeric", task.generate_example()) == 0.0
    assert task.score_answer(5, task.generate_example()) == 0.0
