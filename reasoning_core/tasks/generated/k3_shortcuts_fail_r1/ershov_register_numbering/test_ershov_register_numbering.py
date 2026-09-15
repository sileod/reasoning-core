import random

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.ershov_register_numbering.ershov_register_numbering import (
    ErshovConfig,
    ErshovRegisterNumbering,
    _ershov_numbers,
    _optimal_order,
)


def test_gold_answer_scores_1():
    random.seed(0)
    task = ErshovRegisterNumbering()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_0():
    random.seed(1)
    task = ErshovRegisterNumbering()
    for _ in range(5):
        e = task.generate_example()
        assert task.score_answer("", e) == 0.0
        assert task.score_answer(None, e) == 0.0
        assert task.score_answer("garbage", e) == 0.0


def test_all_levels_generate():
    random.seed(2)
    task = ErshovRegisterNumbering()
    for level in range(7):
        task.config.set_level(level)
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_min_registers_domain():
    random.seed(3)
    task = ErshovRegisterNumbering()
    for level in range(7):
        task.config.set_level(level)
        e = task.generate_example()
        assert e.metadata["min_registers"] >= 1


def test_register_verification():
    random.seed(4)
    task = ErshovRegisterNumbering()
    for _ in range(30):
        e = task.generate_example()
        tree = e.metadata["tree"]
        # independent recursive Ershov computation (Sethi-Ullman recurrence)
        def rec(nid):
            c = tree[nid]
            if c is None:
                return 1
            a = rec(c[0])
            b = rec(c[1])
            return a + 1 if a == b else max(a, b)

        assert rec(str(e.metadata["root"])) == e.metadata["min_registers"]
