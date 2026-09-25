import random

from reasoning_core.tasks.generated.ua_parsing_and_agreement_r4.switch_reference_chains.switch_reference_chains import (
    SwitchReferenceChains,
    SwitchRefConfig,
    compute_answer,
    NAMES,
)

CLASS = SwitchReferenceChains


def test_example_generates():
    random.seed(0)
    task = SwitchReferenceChains()
    ex = task.generate_example()
    assert isinstance(ex.metadata, dict)
    assert "answer" in ex.metadata
    assert len(ex.answer) > 0


def test_answer_matches_gold():
    random.seed(1)
    task = SwitchReferenceChains()
    for _ in range(200):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_compute_answer_matches_roles():
    random.seed(2)
    task = SwitchReferenceChains()
    for _ in range(100):
        ex = task.generate_example()
        roles = ex.metadata["clause_roles"]
        manual = []
        prev = roles[0]["subject"]
        for r in roles[1:]:
            manual.append("same-subject" if r["subject"] == prev else "different-subject")
            prev = r["subject"]
        assert ",".join(manual) == ex.answer


def test_wrong_answers_rejected():
    random.seed(3)
    task = SwitchReferenceChains()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    n_gaps = ex.metadata["n_clauses"] - 1
    wrong = ",".join(["different-subject"] * n_gaps)
    if wrong != ex.answer:
        assert task.score_answer(wrong, ex) == 0.0


def test_labels_balanced():
    random.seed(4)
    task = SwitchReferenceChains()
    counts = {"same-subject": 0, "different-subject": 0}
    for _ in range(500):
        ex = task.generate_example()
        for tok in ex.answer.split(","):
            counts[tok] += 1
    total = sum(counts.values())
    assert total > 0
    assert 0.4 <= counts["same-subject"] / total <= 0.6


def test_config_difficulty():
    cfg = SwitchRefConfig()
    cfg.set_level(0)
    l0 = cfg.n_clauses
    cfg2 = SwitchRefConfig()
    cfg2.set_level(6)
    assert cfg2.n_clauses >= l0
