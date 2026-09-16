from reasoning_core.tasks.generated.k3_scope_and_binding_r1.adjective_inference_modes.adjective_inference_modes import (
    AdjectiveInferenceModes,
    DROP,
    SWAP,
    CONJ,
    MODES,
    make_answer,
    parse_answer,
)


def test_gold_answer_scores_one():
    task = AdjectiveInferenceModes()
    for level in range(7):
        task.config.set_level(level)
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_mode_answers_distinct():
    answers = {make_answer(m) for m in MODES}
    assert len(answers) == 3


def test_inference_truth_table():
    assert {m: DROP[m] for m in MODES} == {"intersective": 1, "subsective": 1, "privative": 1}
    assert {m: SWAP[m] for m in MODES} == {"intersective": 1, "subsective": 0, "privative": 0}
    assert {m: CONJ[m] for m in MODES} == {"intersective": 1, "subsective": 1, "privative": 0}


def test_invalid_answers_score_zero():
    task = AdjectiveInferenceModes()
    task.config.set_level(0)
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("XYZ1", entry) == 0.0
    assert task.score_answer("I", entry) == 0.0
    assert task.score_answer("I1234", entry) == 0.0


def test_parse_answer_rejects_bad_format():
    assert parse_answer("I111") == [("I", "111")]
    assert parse_answer("junk") == []
    assert parse_answer("x1") == []


def test_balanced_modes():
    task = AdjectiveInferenceModes()
    task.config.set_level(0)
    counts = {}
    for _ in range(300):
        entry = task.generate_entry()
        mode = entry["metadata"]["instances"][0]["mode"]
        counts[mode] = counts.get(mode, 0) + 1
    for m in MODES:
        assert counts[m] > 50, counts


def test_difficulty_increases_instances():
    task = AdjectiveInferenceModes()
    task.config.set_level(6)
    assert task.config.n_instances > 1
