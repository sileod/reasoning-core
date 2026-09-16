import random
from fractions import Fraction

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.extensive_form_to_bimatrix.extensive_form_to_bimatrix import (
    ExtensiveFormToBimatrix,
    ExtensiveBimatrixConfig,
    _build_instance,
    _compute_matrix,
    _format_answer,
    _render_tree,
    _term_expected,
    _fmt_frac,
)


def test_smoke_default():
    random.seed(1)
    task = ExtensiveFormToBimatrix()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_matrix_dims_default():
    random.seed(7)
    task = ExtensiveFormToBimatrix()
    task.config.set_level(0)
    x = task.generate_example()
    m = x.metadata["matrix"]
    assert len(m) == x.metadata["b1"]
    assert all(len(r) == x.metadata["b2"] ** x.metadata["b1"] for r in m)


def test_all_levels_generate_and_score():
    random.seed(3)
    task = ExtensiveFormToBimatrix()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(15):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0
            for row in x.metadata["matrix"]:
                for cell in row:
                    assert isinstance(cell, str)
                    assert cell.startswith("(") and cell.endswith(")")


def test_wrong_answers_score_zero():
    random.seed(2)
    task = ExtensiveFormToBimatrix()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer("(0,0)", x) == 0.0
    assert task.score_answer(x.answer + " ;", x) == 0.0


def test_known_small_matrix():
    b1, b2 = 2, 2
    p2 = [[
        ("pay", (3, 1)),
        ("pay", (0, 2)),
    ], [
        ("pay", (5, 0)),
        ("pay", (1, 4)),
    ]]
    m = _compute_matrix(b1, b2, p2)
    for row in m:
        assert all(isinstance(e1, Fraction) and isinstance(e2, Fraction) for e1, e2 in row)
    # row 0 (P1 takes branch 1, path uses P2 node #1): action is tup[0]
    assert m[0][0] == (Fraction(3), Fraction(1))  # tup[0]=0
    assert m[0][2] == (Fraction(0), Fraction(2))  # tup[0]=1 (j=2 -> tup=(1,0))
    # find column index whose node-#1 action=0 and node-#2 action=1
    jj = None
    for j in range(4):
        tu = tuple((j // (2 ** (1 - k))) % 2 for k in range(2))
        if tu == (0, 1):
            jj = j
    assert jj == 1
    assert m[1][jj] == (Fraction(1), Fraction(4))


def test_lottery_expectation():
    t = ("lot", [(1, (5, 0)), (1, (1, 4))], 2)
    e = _term_expected(t)
    assert e == (Fraction(3), Fraction(2))


def test_lottery_three():
    t = ("lot", [(1, (5, 0)), (2, (1, 4))], 3)
    e = _term_expected(t)
    assert e == (Fraction(7, 3), Fraction(8, 3))


def test_format_answer():
    m = [[(Fraction(3), Fraction(1)), (Fraction(0), Fraction(2))]]
    assert _format_answer(m) == "(3,1) | (0,2)"


def test_fmt_frac():
    assert _fmt_frac(Fraction(5)) == "5"
    assert _fmt_frac(Fraction(5, 2)) == "5/2"
    assert _fmt_frac(Fraction(-2, 4)) == "-1/2"


def test_chance_variety_present():
    random.seed(5)
    task = ExtensiveFormToBimatrix()
    task.config.set_level(3)
    seen_lot = False
    seen_pay = False
    for _ in range(120):
        x = task.generate_example()
        if "/" in x.answer:
            seen_lot = True
        else:
            seen_pay = True
        if seen_lot and seen_pay:
            break
    assert seen_lot and seen_pay


def test_no_constant_answer():
    random.seed(9)
    task = ExtensiveFormToBimatrix()
    for level in (0, 3, 6):
        task.config.set_level(level)
        answers = set()
        for _ in range(60):
            x = task.generate_example()
            answers.add(x.answer)
        assert len(answers) > 5


def test_config_scaling():
    c = ExtensiveBimatrixConfig()
    c.set_level(0)
    lo = c.branch_max
    c2 = ExtensiveBimatrixConfig()
    c2.set_level(6)
    assert c2.branch_max > lo
    assert c2.payoff_max > c.payoff_max


def test_validate():
    task = ExtensiveFormToBimatrix()
    task.validate()
