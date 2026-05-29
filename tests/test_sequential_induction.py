import sympy as sp

from reasoning_core.tasks.sequential_induction import format_additive_normal_form


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
