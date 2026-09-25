import random

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.shared_term_congruence.shared_term_congruence import (
    SharedTermCongruence,
)


def _norm(text):
    return "".join(str(text).replace(",", " ").split()).upper()


def test_gold_answer_scores_one_all_levels():
    task = SharedTermCongruence()
    for level in range(0, 7):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_does_not_score_one():
    task = SharedTermCongruence()
    ex = task.generate_example()
    assert task.score_answer("", ex) != 1.0
    assert task.score_answer("zzz", ex) != 1.0


def test_answer_is_tf_string():
    task = SharedTermCongruence()
    ex = task.generate_example()
    assert set(ex.answer) <= {"T", "F"}
    assert len(ex.answer) == len(ex.metadata["queries"])
    assert "T" in ex.answer and "F" in ex.answer


def test_labels_match_query_relations():
    task = SharedTermCongruence()
    from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.shared_term_congruence.shared_term_congruence import (
        _congruence,
    )
    ex = task.generate_example()
    cl = _congruence(
        list(ex.metadata["constants"])
        + [q[0] for q in ex.metadata["queries"]]
        + [q[1] for q in ex.metadata["queries"]],
        [tuple(e) for e in ex.metadata["equalities"]],
    )
    for (a, b), want, ch in zip(
        ex.metadata["queries"], ex.metadata["labels"], ex.answer
    ):
        assert (cl[a] == cl[b]) == want
        assert ("T" if want else "F") == ch


def test_deterministic_under_fixed_seed():
    random.seed(12345)
    task = SharedTermCongruence()
    a = task.generate_example()
    random.seed(12345)
    task2 = SharedTermCongruence()
    b = task2.generate_example()
    assert _norm(a.answer) == _norm(b.answer)


def test_prompt_states_everything():
    task = SharedTermCongruence()
    ex = task.generate_example()
    p = task.render_prompt(ex.metadata)
    assert "congruence closure" in p
    assert "T" in p or "F" in p
