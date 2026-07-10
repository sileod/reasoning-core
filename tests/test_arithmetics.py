from reasoning_core.template import Problem
from reasoning_core.tasks.arithmetics import Arithmetics, fill_num


def test_arithmetics_number_theory_ops():
    task = Arithmetics()
    expr, value = fill_num(
        "gcd(INT, INT) + lcm(POS, POS) + bit_count(NAT) + "
        "is_prime(NAT) + prime_count(NAT) + num_divisors(POS)"
    )
    problem = Problem({"expr": expr, "cot": task.get_cot(expr)}, str(value))

    assert task.score_answer(problem.answer, problem) == 1
    assert all(
        op in problem.metadata.cot
        for op in ("gcd", "lcm", "bit_count", "is_prime", "prime_count", "num_divisors")
    )


def test_floor_division_cot_formats_integer_result():
    assert Arithmetics().get_cot("5 // 2") == "5 // 2 = 2"
