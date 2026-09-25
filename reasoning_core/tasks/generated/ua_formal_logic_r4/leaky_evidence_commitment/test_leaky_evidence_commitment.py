import random

from reasoning_core.tasks.generated.ua_formal_logic_r4.leaky_evidence_commitment.leaky_evidence_commitment import (
    LeakyEvidenceCommitment,
)


def _score(task, answer, entry):
    return task.score_answer(answer, entry)


def test_score_gold():
    task = LeakyEvidenceCommitment()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_score_junk_zero():
    task = LeakyEvidenceCommitment()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("bogus text here", x) == 0.0


def test_score_wrong_choice():
    task = LeakyEvidenceCommitment()
    x = task.generate_example()
    correct, t = x.answer.split()
    wrong = "upper" if correct == "lower" else "lower"
    assert task.score_answer(f"{wrong} {t}", x) == 0.0


def test_score_wrong_steps():
    task = LeakyEvidenceCommitment()
    for _ in range(20):
        x = task.generate_example()
        hit, t = x.answer.split()
        wrong_t = int(t) + 1
        if wrong_t < 1:
            wrong_t = 1
        assert task.score_answer(f"{hit} {wrong_t}", x) == 0.0


def test_difficulty_changes():
    cfg = LeakyEvidenceCommitment().config
    cfg_level0 = LeakyEvidenceCommitment().config
    cfg_level0.set_level(0)
    cfg_level6 = LeakyEvidenceCommitment().config
    cfg_level6.set_level(6)
    assert cfg_level6.max_signs > cfg_level0.max_signs
    assert cfg_level6.bound_high > cfg_level0.bound_high


def test_answer_format_valid():
    task = LeakyEvidenceCommitment()
    for _ in range(50):
        x = task.generate_example()
        parts = x.answer.split()
        assert len(parts) == 2
        assert parts[0] in ("upper", "lower")
        assert parts[1].isdigit()
        assert int(parts[1]) >= 1


def test_levels_supported():
    task = LeakyEvidenceCommitment()
    for level in range(7):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_reproducible_under_seed():
    task = LeakyEvidenceCommitment()
    task.config.set_level(3)
    random.seed(12345)
    answers1 = [task.generate_example().answer for _ in range(5)]
    random.seed(12345)
    answers2 = [task.generate_example().answer for _ in range(5)]
    assert answers1 == answers2
