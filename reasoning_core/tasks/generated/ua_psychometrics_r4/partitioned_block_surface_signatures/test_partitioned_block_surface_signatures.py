from reasoning_core.tasks.generated.ua_psychometrics_r4.partitioned_block_surface_signatures.partitioned_block_surface_signatures import (
    PartitionedBlockSurfaceSignatures,
)


def test_generate_and_score():
    task = PartitionedBlockSurfaceSignatures()
    for level in range(7):
        for _ in range(30):
            entry = task.generate_example(level=level)
            assert task.score_answer(entry.answer, entry) == 1.0
            assert 0 <= int(entry.answer)


def test_label_variety():
    task = PartitionedBlockSurfaceSignatures()
    answers = set()
    for _ in range(100):
        entry = task.generate_example(level=3)
        answers.add(entry.answer)
    assert len(answers) >= 2


def test_junk_scores_zero():
    task = PartitionedBlockSurfaceSignatures()
    entry = task.generate_example(level=2)
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("banana", entry) == 0.0


def test_answers_balanced_across_range():
    task = PartitionedBlockSurfaceSignatures()
    answers = [int(task.generate_example(level=4).answer) for _ in range(60)]
    assert len(set(answers)) >= 3
    assert max(answers) - min(answers) <= 2
