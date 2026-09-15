import random

from reasoning_core.tasks.generated.k3_representation_transfer_r1.critical_pair_generation.critical_pair_generation import (
    CriticalPairGeneration,
    parse,
    subterm_at,
    replace_at,
    apply_subst,
    unify,
    render,
    gather_vars,
    gather_heads,
)


def _task():
    return CriticalPairGeneration()


def test_roundtrip_gold_scores_one():
    random.seed(1)
    t = _task()
    for lvl in range(7):
        t.config.set_level(lvl)
        for _ in range(50):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_junk_and_empty_score_zero():
    random.seed(2)
    t = _task()
    t.config.set_level(0)
    ex = t.generate_example()
    assert t.score_answer("NONE", ex) == (1.0 if ex.answer == "NONE" else 0.0)
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("garbage", ex) == 0.0
    assert t.score_answer(None, ex) == 0.0


def test_both_labels_appear():
    random.seed(3)
    t = _task()
    t.config.set_level(3)
    n_overlap = sum(1 for _ in range(200)
                    if t.generate_example().answer != "NONE")
    assert 110 < n_overlap < 170, n_overlap
    assert n_overlap < 200


def test_no_level_produces_only_one_answer():
    random.seed(4)
    t = _task()
    for lvl in range(7):
        t.config.set_level(lvl)
        answers = set(t.generate_example().answer for _ in range(60))
        assert len(answers) > 1, (lvl, answers)


def test_overlap_answer_is_verbatim_critical_pair():
    random.seed(5)
    t = _task()
    t.config.set_level(2)
    for _ in range(50):
        ex = t.generate_example()
        if ex.answer == "NONE":
            continue
        lhs_a = parse(ex.metadata["a_lhs"])
        lhs_b = parse(ex.metadata["b_lhs"])
        rhs_a = parse(ex.metadata["a_rhs"])
        rhs_b = parse(ex.metadata["b_rhs"])
        path = tuple(ex.metadata["path"])
        sub = subterm_at(lhs_a, path)
        mgu = {}
        assert unify(lhs_b, sub, mgu), ex.answer
        t_a = render(apply_subst(rhs_a, mgu))
        t_b = render(replace_at(apply_subst(lhs_a, mgu), path,
                                apply_subst(rhs_b, mgu)))
        assert ex.answer == f"{t_a} ; {t_b}", ex.answer


def test_none_answer_has_no_head_symbol_overlap():
    random.seed(6)
    t = _task()
    t.config.set_level(2)
    for _ in range(50):
        ex = t.generate_example()
        if ex.answer != "NONE":
            continue
        lhs_a = parse(ex.metadata["a_lhs"])
        lhs_b = parse(ex.metadata["b_lhs"])
        assert lhs_b[0] == "fun" and lhs_b[1] not in gather_heads(lhs_a)


def test_full_coverage_levels():
    random.seed(7)
    t = _task()
    for lvl in [0, 2, 5]:
        t.config.set_level(lvl)
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1.0
        for _ in range(10):
            assert t.score_answer("garbage", t.generate_example()) == 0.0
