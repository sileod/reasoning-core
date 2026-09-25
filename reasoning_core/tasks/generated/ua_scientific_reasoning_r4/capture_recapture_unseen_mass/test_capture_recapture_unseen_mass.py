from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.capture_recapture_unseen_mass import (
    capture_recapture_unseen_mass as mod,
)


def test_gold_roundtrip():
    task = mod.CaptureRecaptureUnseenMass()
    for _ in range(50):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_overlap_recount_consistency():
    task = mod.CaptureRecaptureUnseenMass()
    for _ in range(30):
        x = task.generate_example()
        n1, n2, m = mod.overlap_count(x.metadata["list_a"], x.metadata["list_b"])
        assert n1 == x.metadata["n1"]
        assert n2 == x.metadata["n2"]
        assert m == x.metadata["m"]


def test_estimate_domain():
    task = mod.CaptureRecaptureUnseenMass()
    for _ in range(30):
        x = task.generate_example()
        n_est = int(x.answer)
        union = x.metadata["n1"] + x.metadata["n2"] - x.metadata["m"]
        assert n_est >= union
        assert n_est >= 0


def test_junk_scores_zero():
    task = mod.CaptureRecaptureUnseenMass()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("abc", x) == 0.0
    assert task.score_answer(str(int(x.answer) + 1), x) == 0.0


def test_difficulty_changes_config():
    task = mod.CaptureRecaptureUnseenMass()
    task.config.set_level(0)
    lo0 = (task.config.n1_lo, task.config.n1_hi)
    task.config.set_level(6)
    assert task.config.n1_lo > lo0[0]
    assert task.config.n1_hi > lo0[1]
