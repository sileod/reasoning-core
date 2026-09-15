import random

from reasoning_core.tasks.generated.k3_representation_specific_r1.lie_bracket_hall_normal_form.lie_bracket_hall_normal_form import (
    LieBracketHallNormalForm, LieHallConfig, _parse_linear, _expand, _tree_poly,
)


def _make(level):
    cfg = LieHallConfig()
    cfg.set_level(level)
    task = LieBracketHallNormalForm()
    task.config = cfg
    return task


def test_generates_across_levels():
    task = LieBracketHallNormalForm()
    for level in (0, 1, 2, 3, 4, 5, 6):
        cfg = LieHallConfig()
        cfg.set_level(level)
        task.config = cfg
        ex = task.generate_example()
        assert ex.answer
        assert isinstance(ex.metadata.expr, str)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_roundtrip_and_reject_garbage():
    task = LieBracketHallNormalForm()
    for level in (0, 2, 5, 6):
        cfg = LieHallConfig()
        cfg.set_level(level)
        task.config = cfg
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("0", ex) < 1.0
        assert task.score_answer("bogus", ex) == 0.0


def test_domain_answer_is_valid_linear_combination():
    task = LieBracketHallNormalForm()
    cfg = LieHallConfig()
    cfg.set_level(5)
    task.config = cfg
    for _ in range(20):
        ex = task.generate_example()
        if ex.answer == "0":
            continue
        parsed = _parse_linear(ex.answer)
        assert parsed, "answer must be a nonzero linear combination"


def test_deterministic_under_seed():
    task = LieBracketHallNormalForm()
    random.seed(7)
    cfg = LieHallConfig()
    cfg.set_level(3)
    task.config = cfg
    a1 = task.generate_example().answer
    random.seed(7)
    cfg = LieHallConfig()
    cfg.set_level(3)
    task.config = cfg
    a2 = task.generate_example().answer
    assert a1 == a2


def test_prompt_mentions_class_and_basis():
    task = LieBracketHallNormalForm()
    cfg = LieHallConfig()
    cfg.set_level(4)
    task.config = cfg
    ex = task.generate_example()
    p = task.render_prompt(ex.metadata)
    assert str(ex.metadata.c) in p
    assert "[X1,X2]" in p
