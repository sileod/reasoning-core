from decimal import Decimal
from fractions import Fraction

from reasoning_core.template import Problem, edict
from reasoning_core.tasks.arithmetics import (
    Arithmetics,
    SAFE_FUNCS,
    _canonical_decimal,
    fill_num,
)


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


def test_python_division_semantics_note_is_contextual():
    task = Arithmetics()

    floor_prompt = task.render_prompt(edict(expr="-7 // 2", digit_mode="normal"))
    modulo_prompt = task.render_prompt(edict(expr="-7 % 3", digit_mode="normal"))
    assert "Python semantics for //." in floor_prompt
    assert "Python semantics for %." in modulo_prompt
    assert "Python semantics" not in task.render_prompt(edict(expr="-7 / 2", digit_mode="normal"))


def test_zero_answers_are_canonical():
    assert _canonical_decimal(Decimal("0.000"), 3) == "0"
    assert _canonical_decimal(Decimal("-0.000"), 3) == "0"


def test_round_is_exact_and_halfway_note_is_contextual():
    task = Arithmetics()

    assert SAFE_FUNCS["round"](Fraction(9_007_199_254_740_997, 2)) == 4_503_599_627_370_498
    tie_prompt = task.render_prompt(edict(expr="round(5 / 2)", digit_mode="normal"))
    non_tie_prompt = task.render_prompt(edict(expr="round(8 / 3)", digit_mode="normal"))
    assert "Round ties" in tie_prompt
    assert "nearest even integer" in tie_prompt
    assert "Round ties" not in non_tie_prompt


def test_prime_functions_use_standard_negative_semantics():
    assert SAFE_FUNCS["is_prime"](-7) == 0
    assert SAFE_FUNCS["prime_count"](-7) == 0
