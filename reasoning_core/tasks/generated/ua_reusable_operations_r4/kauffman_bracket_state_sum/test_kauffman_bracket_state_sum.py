import random

from reasoning_core.tasks.generated.ua_reusable_operations_r4.kauffman_bracket_state_sum.kauffman_bracket_state_sum import (
    KauffmanBracketStateConfig,
    KauffmanBracketStateSum,
    kauffman_contribution,
    monomial_str,
)


def test_generate_example():
    task = KauffmanBracketStateSum()
    for _ in range(20):
        ex = task.generate_example()
        assert ex.answer
        assert task.score_answer(ex.answer, ex) == 1.0


def test_scores():
    task = KauffmanBracketStateSum()
    for _ in range(20):
        ex = task.generate_entry()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("garbage", ex) == 0.0


def test_monomial_str_roundtrip():
    for a in range(6):
        for b in range(6):
            for l in range(4):
                c, e = kauffman_contribution(a, b, l)
                s = monomial_str(c, e)
                c2, e2 = kauffman_contribution(a, b, l)
                assert monomial_str(c2, e2) == s


def test_wrong_answer_rejected():
    task = KauffmanBracketStateSum()
    ex = task.generate_entry()
    ans = ex.answer
    wrong = "A^0" if ans != "1" else "A^1"
    assert task.score_answer(wrong, ex) < 1.0


def test_difficulty_changes():
    base = KauffmanBracketStateConfig()
    base.set_level(6)
    assert base.ncross > 2


def test_metadata_json_serializable():
    import json

    task = KauffmanBracketStateSum()
    ex = task.generate_example()
    json.dumps(ex.metadata)


def test_seed_reproducible():
    random.seed(12345)
    t1 = KauffmanBracketStateSum()
    ex1 = t1.generate_entry().answer
    random.seed(12345)
    t2 = KauffmanBracketStateSum()
    ex2 = t2.generate_entry().answer
    assert ex1 == ex2
