"""Scorer checks for dev/math_inverse: equivalent forms pass, near misses fail. Run as a script."""
import random

from reasoning_core.template import Entry
from reasoning_core.tasks.dev.math_inverse import InverseMath, score_inverse


def s(meta, answer):
    return score_inverse(answer, Entry(metadata=meta, answer=""))


CASES = [
    ({"mode": "integral", "integrand": "1/(x^2 + 1)"}, [("atan(x)", 1), ("atan(x) + 7", 1), ("arctan(x) + C", 1),
                                                       ("F(x) = atan(x)", 1), ("atan(2*x)", 0), ("1/(x^2+1)", 0)]),
    ({"mode": "integral", "integrand": "1/x"}, [("log(x)", 1), ("ln(x)", 1), ("log(3*x)", 1), ("log(x^2)", 0), ("ln|x|", 1), ("ln(abs(x)) + 2", 1)]),
    ({"mode": "integral", "integrand": "tan(x)"}, [("-ln|cos(x)|", 1), ("-log(cos(x))", 1), ("log(cos(x))", 0)]),
    ({"mode": "factor", "poly": "25*x^3 + 20*x^2 + 4*x", "vars": ["x"]},
     [("x*(5*x + 2)^2", 1), ("(5x+2)^2 x", 1), ("x*(5*x+2)*(5*x+2)", 1), ("x*(25*x^2 + 20*x + 4)", 0),
      ("25*x^3 + 20*x^2 + 4*x", 0), ("x*(5*x + 2)^3", 0)]),
    ({"mode": "factor", "poly": "2*x^2 - 2", "vars": ["x"]},
     [("2*(x - 1)*(x + 1)", 1), ("-2*(1 - x)*(x + 1)", 1), ("(2*x - 2)*(x + 1)", 0), ("2*(x^2 - 1)", 0)]),
    ({"mode": "equation", "lhs": "exp(2*x) - 3*exp(x)", "rhs": "-2", "solutions": ["0", "log(2)"]},
     [("0, log(2)", 1), ("ln 2, 0", 1), ("{0, log(2)}", 1), ("x = 0, x = log(2)", 1), ("0", 0), ("0, log(2), 1", 0)]),
    ({"mode": "equation", "lhs": "exp(x)", "rhs": "-1", "solutions": []}, [("none", 1), ("No real solution", 1), ("0", 0)]),
    ({"mode": "recurrence", "order": 2, "rhs": "", "init": [], "values": [str(2 ** i + 1) for i in range(12)]},
     [("2^n + 1", 1), ("1 + 2**n", 1), ("2^n", 0), ("2^(n+1) - 2^n + 1", 1)]),
    ({"mode": "sos", "f": "2*x^2 - 4*x + 5", "bound": "3", "vars": ["x"]},
     [("2*(x - 1)^2", 1), ("(x-1)^2 + (x-1)^2", 1), ("2*(1 - x)^2", 1), ("(x-1)^2/2*4", 1),
      ("2*x^2 - 4*x + 2", 0), ("-2*(x-1)^2 + 4*(x-1)^2", 0), ("2*(x - 1)^3", 0), ("(x - 1)^2", 0)]),
    ({"mode": "sos", "f": "x^6 + 6*x^4 + 9*x^2", "bound": "0", "vars": ["x"]},
     [("x^2*(x^2 + 3)^2", 1), ("(x^3 + 3*x)^2", 1), ("x^2*(x^2 + 3)^3", 0), ("x*(x^2 + 3)^2", 0)]),
    ({"mode": "claim", "f": "2*x^2 - 4*x + 5", "bound": "2", "vars": ["x"]},
     [("proof: 2*(x - 1)^2 + 1", 1), ("Proof: (x-1)^2 + (x-1)^2 + 1", 1), ("proof: 2*(x-1)^2", 0),
      ("counterexample: x = 1", 0), ("true", 0)]),
    ({"mode": "claim", "f": "2*x^2 - 4*x + 5", "bound": "4", "vars": ["x"]},
     [("counterexample: x = 1", 1), ("counterexample: x = 3/2", 1), ("counterexample: x = 0", 0),
      ("proof: 2*(x-1)^2 - 1", 0), ("false", 0)]),
    ({"mode": "eigen", "matrix": "", "eigenvalues": [-1, 2, 2]},
     [("-1, 2, 2", 1), ("2, -1, 2", 1), ("[-1, 2, 2]", 1), ("-1, 2", 0), ("-1, 2, 3", 0)]),
    ({"mode": "ideal", "f1": "x - y", "f2": "x + y", "g": "x^2 - y^2 + 2*x"},
     [("a = x + y + 1, b = 1", 1), ("a = x + 1 + y, b = 1", 1), ("a=(x+y+1), b=1", 1), ("b = 1, a = x + y + 1", 1),
      ("a = x + y, b = 1", 0), ("a = x + y + 1", 0), ("x + y + 1, 1", 0)]),
    ({"mode": "minimum", "f": "2*x^2 - 4*x + 5", "vars": ["x"], "min": "3"}, [("3", 1), ("3.0", 1), ("1", 0), ("x", 0)]),
    ({"mode": "sum", "term": "1/(k*(k + 1))"}, [("n/(n + 1)", 1), ("1 - 1/(n+1)", 1), ("(n-1)/n", 0)]),
]


def _ode_meta():
    import sympy as sp
    from reasoning_core.tasks.dev.math_inverse import Y, x
    return {"mode": "ode", "ode": "y' = y", "ode_lhs": sp.srepr(sp.Derivative(Y(x), x) - Y(x))}


ODE = [("C*exp(x)", 1), ("y = C*e^x", 1), ("exp(x + C)", 1), ("exp(x)", 0), ("C*exp(2*x)", 0), ("C + exp(x)", 0)]


def _ode2_meta():
    import sympy as sp
    from reasoning_core.tasks.dev.math_inverse import Y, x
    lhs = sp.Derivative(Y(x), (x, 2)) - 3 * sp.Derivative(Y(x), x) + 2 * Y(x) - 2 * x + 3
    return {"mode": "ode", "order": 2, "ode": "", "ode_lhs": sp.srepr(lhs)}


ODE2 = [("C1*exp(x) + C2*exp(2*x) + x", 1), ("C2*exp(x) + C1*exp(2*x) + x", 1), ("C1*exp(x) + C2*exp(x) + x", 0),
        ("C1*exp(x) + x", 0), ("C1*exp(x) + C2*exp(2*x)", 0), ("(C1 + C2)*exp(x) + x", 0), ("C_1 e^x + C_{2} e^{2x} + x", 1)]


def main():
    bad = 0
    for meta, answers in CASES:
        for answer, want in answers:
            got = s(meta, answer)
            if got != want:
                bad += 1
                print(f"MISMATCH {meta['mode']}: {answer!r} scored {got}, expected {want}")
    for answer, want in ODE:
        got = s(_ode_meta(), answer)
        if got != want:
            bad += 1
            print(f"MISMATCH ode: {answer!r} scored {got}, expected {want}")
    for answer, want in ODE2:
        got = s(_ode2_meta(), answer)
        if got != want:
            bad += 1
            print(f"MISMATCH ode2: {answer!r} scored {got}, expected {want}")
    random.seed(0)
    task = InverseMath()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(30):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1, e
            assert task.score_answer("x", e) == 0 and task.score_answer("0", e) == 0 or e.answer in ("x", "0"), e
    print("mismatches:", bad)


if __name__ == "__main__":
    main()
