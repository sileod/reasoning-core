"""Scorer checks for dev/planted_witness: equivalent forms pass, near misses fail. Run as a script."""
import random

import sympy as sp

from reasoning_core.tasks.generated.planted_witness import PlantedWitness, _rhs, encode, n, score_witness, x


def meta(kind, names, terms, W):
    return {"kind": kind, "unknowns": names, "equations": [],
            "terms": [encode(t) for t in terms], "rhs": [sp.srepr(_rhs(t, W, kind)) for t in terms]}


CASES = [
    (meta("polynomial", ["p", "q"], [("mul", ("u", 0, x), ("u", 1, x + 1)), ("add", ("u", 0, x), ("u", 1, sp.Integer(0)))],
          [2 * x + 1, x - 3]),
     [("p(x) = 2*x + 1, q(x) = x - 3", 1), ("q(x) = x - 3, p(x) = 1 + 2x", 1), ("p(x)=2x+1 and q(x)=x-3", 1),
      ("$p(x) = 2x + 1$, $q(x) = x - 3$", 1), ("p(x) = 2*x + 1", 0), ("p(x) = 2*x, q(x) = x - 3", 0),
      ("p(x) = x + 1/2, q(x) = 2*x - 6", 0)]),
    (meta("sequence", ["a"], [("add", ("u", 0, n), ("u", 0, n))], [3 * 2 ** n + 1]),
     [("a(n) = 3*2^n + 1", 1), ("a(n) = 3 \\cdot 2^{n} + 1", 1), ("a(n) = 2^n + 2^(n+1) + 1", 1), ("a(n) = 3*2^n", 0)]),
    (meta("number", ["X", "Y"], [("add", ("u", 0, None), ("u", 1, None)), ("mul", ("u", 0, None), ("u", 1, None))],
          [sp.Integer(2), sp.Integer(5)]),
     [("X = 2, Y = 5", 1), ("Y = 5, X = 2", 1), ("X = 5, Y = 2", 1), ("X = 2", 0), ("X = 2, Y = 4", 0)]),
]


def main():
    bad = 0
    for m, answers in CASES:
        for answer, want in answers:
            got = score_witness(answer, {"metadata": m})
            if got != want:
                bad += 1
                print(f"MISMATCH {m['kind']}: {answer!r} scored {got}, expected {want}")
    random.seed(0)
    task = PlantedWitness()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(15):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1, e
            assert task.score_answer(e.answer.replace("=", "= 1 +", 1), e) == 0, e
    print("mismatches:", bad)


if __name__ == "__main__":
    main()
