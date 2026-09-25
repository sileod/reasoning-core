import random
import re

from reasoning_core.tasks.generated.ua_formal_logic_r4.finite_order_gap_elimination.finite_order_gap_elimination import (
    FiniteOrderGapElimination,
    _eliminate,
)


def test_eliminate_matches_answer():
    metadata = {
        "n": 3,
        "names": ["x0", "x1", "x2"],
        "split": 1,
        "a": 2,
        "b": 3,
    }
    assert _eliminate(metadata) == "x0 < x1 & x2 - x1 = 5"
    metadata2 = dict(metadata, split=0, a=1, b=1)
    assert _eliminate(metadata2) == "x1 - x0 = 2 & x1 < x2"


def test_scores():
    task = FiniteOrderGapElimination()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0


def test_answer_format():
    task = FiniteOrderGapElimination()
    ex = task.generate_example()
    atoms = ex.answer.split(" & ")
    assert all(re.match(r"^x\d+ < x\d+$", at) or re.match(r"^x\d+ - x\d+ = \d+$", at) for at in atoms)


def test_difficulty_changes():
    task = FiniteOrderGapElimination()
    task.config.set_level(0)
    n0 = task.config.nvars
    task.config.set_level(6)
    assert task.config.nvars > n0


def test_reproducible():
    random.seed(123)
    t = FiniteOrderGapElimination()
    t.config.set_level(3)
    a = t.generate_entry().answer
    random.seed(123)
    t2 = FiniteOrderGapElimination()
    t2.config.set_level(3)
    b = t2.generate_entry().answer
    assert a == b
