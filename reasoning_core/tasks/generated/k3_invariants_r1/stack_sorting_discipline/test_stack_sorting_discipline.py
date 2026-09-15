import random

from reasoning_core.tasks.generated.k3_invariants_r1.stack_sorting_discipline.stack_sorting_discipline import (
    StackSortingDiscipline, StackSortingConfig, _simulate, design_choice)


def test_round_trip():
    task = StackSortingDiscipline()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_gold_scores_one_all_levels():
    task = StackSortingDiscipline()
    for level in range(7):
        cfg = StackSortingConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(30):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_garbage_scores_zero():
    task = StackSortingDiscipline()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("junk", x) == 0.0
    assert task.score_answer("1.5", x) == 0.0
    assert task.score_answer(" 5", x) == 0.0


def test_wrong_answer_zero():
    task = StackSortingDiscipline()
    for _ in range(40):
        x = task.generate_example()
        wrong = set(range(1, len(x.metadata.perm) + 1)) - {int(x.answer)}
        if wrong:
            bad = wrong.pop()
            assert task.score_answer(str(bad), x) == 0.0


def test_difficulty_changes():
    c0 = StackSortingConfig().set_level(0)
    c6 = StackSortingConfig().set_level(6)
    assert c6.n > c0.n


def test_answer_varies():
    task = StackSortingDiscipline()
    cfg = StackSortingConfig()
    cfg.set_level(5)
    task.config = cfg
    answers = set()
    for _ in range(120):
        x = task.generate_example()
        answers.add(x.answer)
    assert len(answers) >= 8


def test_both_answer_semantics_present():
    task = StackSortingDiscipline()
    kth = 0
    blk = 0
    for _ in range(200):
        x = task.generate_example()
        pops, blocked = _simulate(x.metadata.perm)
        if x.metadata.k <= len(pops):
            kth += 1
        else:
            blk += 1
    assert kth > 10 and blk > 10


def test_blocked_answer_is_stack_top():
    task = StackSortingDiscipline()
    for _ in range(200):
        x = task.generate_example()
        pops, blocked = _simulate(x.metadata.perm)
        if x.metadata.k > len(pops):
            assert int(x.answer) == blocked


def test_design_choice_verbatim():
    assert design_choice.startswith("Return the element popped at the k-th pop")


def test_deterministic_samily_mode_no_reseed():
    random.seed(12345)
    task = StackSortingDiscipline()
    a1 = [task.generate_example().answer for _ in range(20)]
    random.seed(12345)
    a2 = [task.generate_example().answer for _ in range(20)]
    assert a1 == a2
