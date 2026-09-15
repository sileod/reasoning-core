from reasoning_core.tasks.generated.k3_uncertainty_r1.threshold_share_reconstruction.threshold_share_reconstruction import (
    ThresholdShareReconstruction,
    PRIMES,
)


def test_gold_answer_scores_one():
    task = ThresholdShareReconstruction()
    for _ in range(20):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_wrong_answer_scores_zero():
    task = ThresholdShareReconstruction()
    for _ in range(20):
        entry = task.generate_example()
        wrong = str((int(entry.answer) + 1) % entry.metadata["prime"])
        assert task.score_answer(wrong, entry) != 1.0


def test_difficulty_changes_config():
    task = ThresholdShareReconstruction()
    c0 = ThresholdShareReconstruction.config_cls()
    c0.set_level(0)
    c6 = ThresholdShareReconstruction.config_cls()
    c6.set_level(6)
    assert (c6.degree, c6.present) != (c0.degree, c0.present)
    assert c6.degree >= c0.degree
    assert c6.present >= c0.present


def test_answer_within_domain():
    task = ThresholdShareReconstruction()
    for _ in range(20):
        entry = task.generate_example()
        p = entry.metadata["prime"]
        ans = int(entry.answer)
        assert 0 <= ans < p


def test_primes_fixed_set():
    task = ThresholdShareReconstruction()
    for _ in range(30):
        entry = task.generate_example()
        assert entry.metadata["prime"] in PRIMES
