from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r1.modal_negation_equivalence.modal_negation_equivalence import (
    ModalNegationEquivalence,
)


def test_generate_example():
    task = ModalNegationEquivalence()
    ex = task.generate_example()
    assert ex.answer in ["must", "must not", "may", "may not"]
    assert ex.metadata["canonical"] == ex.answer
    assert ex.metadata["force"] in ["must", "may"]
    assert ex.metadata["flavor"] in ["deontic", "epistemic"]


def test_score_gold():
    task = ModalNegationEquivalence()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_score_wrong():
    task = ModalNegationEquivalence()
    for _ in range(50):
        ex = task.generate_example()
        wrong = {"must", "must not", "may", "may not"} - {ex.answer}
        for w in wrong:
            assert task.score_answer(w, ex) == 0.0


def test_score_junk():
    task = ModalNegationEquivalence()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage words here", ex) == 0.0


def test_difficulty_changes_config():
    task = ModalNegationEquivalence()
    task.config.set_level(0)
    l0 = task.config.flavor
    task.config.set_level(6)
    l6 = task.config.flavor
    assert l0 != l6


def test_answer_balance_across_levels():
    task = ModalNegationEquivalence()
    for level in (0, 2, 5):
        task.config.set_level(level)
        seen = {}
        for _ in range(200):
            ex = task.generate_example()
            seen[ex.answer] = seen.get(ex.answer, 0) + 1
        assert len(seen) == 4, f"level {level} answers: {seen}"
