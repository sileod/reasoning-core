import random

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.shifted_consensus_reconstruction.shifted_consensus_reconstruction import (
    ShiftedConsensusReconstruction,
)


def test_gold_answer_scores_1():
    random.seed(1)
    task = ShiftedConsensusReconstruction()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_score_0():
    random.seed(2)
    task = ShiftedConsensusReconstruction()
    ex = task.generate_example()
    gold = ex.metadata["source"]
    wrong = "A" * len(gold) if gold != "A" * len(gold) else "C" * len(gold)
    assert task.score_answer(wrong, ex) == 0.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer(123, ex) == 0.0


def test_difficulty_changes_config():
    task = ShiftedConsensusReconstruction()
    base = task.config.source_len
    task.config.set_level(5)
    assert task.config.source_len > base


def test_consensus_matches_source():
    random.seed(3)
    task = ShiftedConsensusReconstruction()
    for _ in range(30):
        ex = task.generate_example()
        assert ex.metadata["source"] == ex.answer


def test_all_levels_generate():
    task = ShiftedConsensusReconstruction()
    for level in range(0, 7):
        task.config.set_level(level)
        random.seed(100 + level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_no_constant_answer_at_level():
    task = ShiftedConsensusReconstruction()
    for level in (0, 3, 6):
        task.config.set_level(level)
        random.seed(5000 + level)
        answers = set()
        for _ in range(20):
            answers.add(task.generate_example().answer)
        assert len(answers) > 3


def test_copies_consistent_with_offset():
    random.seed(7)
    task = ShiftedConsensusReconstruction()
    ex = task.generate_example()
    source = ex.metadata["source"]
    for L, off in zip(ex.metadata["copies"], ex.metadata["offsets"]):
        for j, ch in enumerate(L):
            src_pos = j - off
            if 0 <= src_pos < len(source):
                assert source[src_pos] == ch or in_mismatch(ex, j)


def in_mismatch(ex, j):
    for mm in ex.metadata["mismatch_positions"]:
        if j in mm:
            return True
    return False
