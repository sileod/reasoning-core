from reasoning_core.tasks.generated.k3_verification_repair_r1.mealy_composition_run.mealy_composition_run import (
    MealyCompositionRun,
)


def test_gold_scores_one():
    task = MealyCompositionRun()
    for level in (0, 2, 5, 6):
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0, (level, ex.answer)


def test_garbage_scores_zero():
    task = MealyCompositionRun()
    ex = task.generate_example()
    for bad in ("", "garbage", "abc;1", "abc;x;y", "abc;1;2;3"):
        assert task.score_answer(bad, ex) == 0.0, bad


def test_answer_matches_metadata():
    task = MealyCompositionRun()
    for level in (0, 3, 6):
        ex = task.generate_example(level=level)
        w, sa, sb = ex.answer.split(";")
        assert w == ex.metadata["answer_word"]
        assert int(sa) == ex.metadata["answer_state_a"]
        assert int(sb) == ex.metadata["answer_state_b"]
        assert sa in ("0", "1", "2", "3")
        assert sb in ("0", "1", "2", "3")


def test_domain_invariants():
    task = MealyCompositionRun()
    for level in (0, 6):
        ex = task.generate_example(level=level)
        alpha = set(ex.metadata["alphabet"])
        assert set(ex.metadata["input_word"]) <= alpha
        assert set(ex.metadata["answer_word"]) <= alpha
        assert ex.metadata["answer_state_a"] < ex.metadata["num_states_a"]
        assert ex.metadata["answer_state_b"] < ex.metadata["num_states_b"]


def test_difficulty_changes_config():
    task = MealyCompositionRun()
    task.config.set_level(0)
    a = (task.config.num_states, task.config.alphabet_size, task.config.word_len)
    task.config.set_level(6)
    b = (task.config.num_states, task.config.alphabet_size, task.config.word_len)
    assert a != b
    assert b[2] > a[2]
