from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.head_splicing_round_closure.head_splicing_round_closure import (
    HeadSplicingRoundClosure,
)


def test_generate_and_score():
    task = HeadSplicingRoundClosure()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_levels_all_produce():
    task = HeadSplicingRoundClosure()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_garbage_scores_zero():
    task = HeadSplicingRoundClosure()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage", ex) < 1.0
    assert task.score_answer("[]", ex) < 1.0


def test_difficulty_changes_config():
    task = HeadSplicingRoundClosure()
    task.config.set_level(0)
    c0 = (task.config.num_starters, task.config.exon_len, task.config.rounds)
    task.config.set_level(6)
    c6 = (task.config.num_starters, task.config.exon_len, task.config.rounds)
    assert c0 != c6
