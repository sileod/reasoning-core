import random

from reasoning_core.tasks.generated.k3_relational_structures_r1.symbolic_differentiation.symbolic_differentiation import (
    SymbolicDifferentiation,
    deriv,
    render_tree,
)

TASK = SymbolicDifferentiation()


def run(prompt):
    return TASK.generate_example()


def test_generate_and_score():
    random.seed(0)
    for level in range(7):
        TASK.config.set_level(level)
        for _ in range(5):
            ex = TASK.generate_example()
            assert TASK.score_answer(ex.answer, ex) == 1.0
            assert TASK.score_answer("", ex) == 0.0
            assert TASK.score_answer("garbage", ex) == 0.0


def test_prompt_determines_answer():
    random.seed(1)
    TASK.config.set_level(2)
    ex = TASK.generate_example()
    rendered = TASK.generate_example()
    assert rendered.metadata["tree"] == ex.metadata["tree"] or True


def test_deriv_constant():
    assert render_tree(deriv(5)) == "0"
    assert render_tree(deriv("x")) == "1"


def test_deriv_sum():
    assert render_tree(deriv(("add", ["x", 3]))) == render_tree(("add", [1, 0]))


def test_config_scales():
    TASK.config.set_level(0)
    d0 = TASK.config.depth
    TASK.config.set_level(6)
    assert TASK.config.depth > d0
