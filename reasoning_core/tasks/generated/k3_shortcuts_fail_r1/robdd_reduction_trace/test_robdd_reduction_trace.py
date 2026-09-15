import random
import re

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.robdd_reduction_trace.robdd_reduction_trace import (
    _parse_expr,
    _truth_table,
    _build_robdd,
    _eval_ite,
    RobddReductionTrace,
    RobddConfig,
)


def _set_seed():
    random.seed(20250101)


def test_gold_scores_one():
    _set_seed()
    task = RobddReductionTrace()
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_robdd_matches_truth():
    _set_seed()
    task = RobddReductionTrace()
    for _ in range(20):
        e = task.generate_example()
        order = e.metadata['order']
        tt = e.metadata['truth_table']
        n = len(order)
        for mask in range(1 << n):
            assert _eval_ite(e.answer, order, mask) == tt[mask], e.answer


def test_junk_scores_zero():
    task = RobddReductionTrace()
    e = task.generate_example()
    assert task.score_answer('', e) == 0.0
    assert task.score_answer('garbage', e) == 0.0
    assert task.score_answer(None, e) == 0.0
    assert task.score_answer(123, e) == 0.0


def test_whitespace_insensitive():
    task = RobddReductionTrace()
    e = task.generate_example()
    with_space = re.sub(r'(?<=[(),])', ' ', e.answer)
    assert task.score_answer(with_space, e) == 1.0


def test_difficulty_changes():
    cfg = RobddConfig()
    cfg.set_level(0)
    assert cfg.n_vars == 2
    cfg.set_level(6)
    assert cfg.n_vars == 6
    assert cfg.max_depth == 9


def test_not_constant():
    _set_seed()
    task = RobddReductionTrace()
    answers = set()
    for _ in range(30):
        e = task.generate_example()
        answers.add(e.answer)
    assert len(answers) > 5


def test_binary_and_or_not_variety():
    _set_seed()
    task = RobddReductionTrace()
    expr_kinds = set()
    for _ in range(20):
        e = task.generate_example()
        expr_kinds.add(e.metadata['expr'])
    assert len(expr_kinds) > 10
