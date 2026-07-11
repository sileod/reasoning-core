import random

from reasoning_core.csp import (
    AllDifferent, Eq, EqVar, Exactly, Implies, Linear, Mod, Ne, Or, Var, Xor,
)
from reasoning_core.csp.metrics import analyze, split_key
from reasoning_core.csp.selection import Query, minimize
from reasoning_core.csp.solver import CSPSolver


def test_ir_canonicalizes_commutative_and_linear_forms():
    x, y = Var("x", range(3)), Var("y", range(3))
    assert EqVar(x, y).canonical() == EqVar(y, x).canonical()
    assert Or((Eq(x, 1), Ne(y, 0))).canonical() == Or((Ne(y, 0), Eq(x, 1))).canonical()
    assert Linear((-2, -4), (x, y), "<=", -6).canonical() == Linear((1, 2), (x, y), ">=", 3).canonical()
    assert Mod(Linear((1,), (x,), "==", 0), 3, 1).canonical() == Mod(Linear((1,), (x,), "!=", 2), 3, 1).canonical()


def test_compositional_formulas_compile_and_solve():
    x, y = Var("x", range(3)), Var("y", range(3))
    formulas = [
        Or((Eq(x, 1), Eq(y, 1))), Xor((Eq(x, 1), Eq(y, 1))),
        Implies(Eq(x, 1), Ne(y, 1)), Exactly(1, (Eq(x, 1), Eq(y, 1))), Ne(y, 1),
    ]
    solver = CSPSolver((x, y), clues=formulas)
    assert solver.unique_value(x) == 1
    assert solver.unique_value(y) != 1


def test_query_aware_minimization_and_metrics_are_semantic():
    x, y, z = (Var(name, range(3)) for name in "xyz")
    base = [AllDifferent((x, y, z))]
    pool = [Ne(x, 0), Ne(x, 2), Eq(y, 0), Eq(z, 2), Ne(y, 2)]
    query = Query("scalar", x, 1, "What is x?")
    selected = minimize(CSPSolver((x, y, z), base), pool, query, random.Random(4), 4)
    assert selected is not None
    assert CSPSolver((x, y, z), base).unique_value(x, selected.clues) == 1
    assert selected.metrics["query_domain_after"] == [1]
    assert selected.metrics["wrong_answer_core_sizes"]


def test_lexicographic_solution_is_not_solver_model_order():
    x, y = Var("x", range(3)), Var("y", range(3))
    solver = CSPSolver((x, y), clues=[Ne(x, y.domain[-1]), Ne(y, 0)])
    assert solver.lex_solution() == (0, 1)


def test_structural_split_key_ignores_formula_argument_order():
    x, y = Var("x", range(2)), Var("y", range(2))
    a = split_key("graph", [AllDifferent((x, y))], [EqVar(x, y)], "scalar")
    b = split_key("graph", [AllDifferent((y, x))], [EqVar(y, x)], "scalar")
    assert a == b
