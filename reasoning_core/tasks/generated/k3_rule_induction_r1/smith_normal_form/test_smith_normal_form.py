import random

from reasoning_core.tasks.generated.k3_rule_induction_r1.smith_normal_form.smith_normal_form import (
    SmithNormalForm,
    _invariant_factors,
    _parse_tuple,
)


def _all_levels():
    task = SmithNormalForm()
    for level in range(7):
        task.config.set_level(level)
        yield level, task


def test_generate_scores_one():
    for level, task in _all_levels():
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
        inv = _parse_tuple(x.answer)
        assert all(f >= 0 for f in inv)


def test_answer_matches_solver():
    for _ in range(20):
        x = SmithNormalForm().generate_example()
        assert _parse_tuple(x.answer) == _invariant_factors(x.metadata["matrix"])


def test_score_rejects_junk():
    task = SmithNormalForm()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer("(abc)", x) == 0.0


def test_score_rejects_wrong_tuple():
    task = SmithNormalForm()
    x = task.generate_example()
    gold = _parse_tuple(x.answer)
    if len(gold) >= 1:
        wrong = tuple(gold[i] + (1 if i == 0 else 0) for i in range(len(gold)))
        if wrong != gold:
            assert task.score_answer(str(wrong), x) == 0.0


def test_reproducible_under_seed():
    random.seed(12345)
    a = SmithNormalForm().generate_example()
    random.seed(12345)
    b = SmithNormalForm().generate_example()
    assert a.prompt == b.prompt
    assert a.answer == b.answer


def test_divisibility_holds():
    for i in range(30):
        inv = _parse_tuple(SmithNormalForm().generate_example().answer)
        for d1, d2 in zip(inv, inv[1:]):
            assert d2 % d1 == 0
