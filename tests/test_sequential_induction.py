import sympy as sp

from reasoning_core.tasks.sequential_induction import Sequence, convert_to_sympy, format_additive_normal_form


def test_additive_normal_form_expands_and_sorts_low_degree_first():
    n = sp.symbols("n", integer=True, nonnegative=True)
    U = sp.IndexedBase("U")

    expr = (n + 8) * (U[n - 2] - 6)

    assert format_additive_normal_form(expr) == (
        "-48 - 6*n + 8*U[n - 2] + n*U[n - 2]"
    )


def test_additive_normal_form_inverts_sympy_polynomial_order():
    n = sp.symbols("n", integer=True, nonnegative=True)

    assert format_additive_normal_form(-n**2 + 2 * n + 1) == "1 + 2*n - n**2"


def test_division_is_not_cancelled_as_rational_arithmetic():
    expr = convert_to_sympy(["(U1 / 2) * 2"], recurrence_depth=1)
    formula = format_additive_normal_form(expr)
    grouped_expr = convert_to_sympy(["(U1 + 1) / 2"], recurrence_depth=1)
    grouped_formula = format_additive_normal_form(grouped_expr)

    assert "//" in formula
    assert Sequence(formula, initial_elem=[3]).n_first_elem(2) == [3, 2]
    assert Sequence(grouped_formula, initial_elem=[2]).n_first_elem(2) == [2, 1]
