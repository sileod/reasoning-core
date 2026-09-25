import random

from reasoning_core.tasks.generated.ua_latent_representation_r4.stereochemical_parity_transport.stereochemical_parity_transport import (
    StereochemicalParityTransport,
)

TASK = StereochemicalParityTransport


def test_generate_and_score():
    task = TASK()
    for _ in range(50):
        x = task.generate_example()
        assert x.answer in ("D", "L")
        assert task.score_answer(x.answer, x) == 1.0
        assert task.score_answer("D" if x.answer == "L" else "L", x) == 0.0
        assert task.score_answer("bogus", x) == 0.0
        assert task.score_answer("", x) == 0.0


def test_label_balance():
    task = TASK()
    counts = {"D": 0, "L": 0}
    for _ in range(200):
        counts[task.generate_example().answer] += 1
    assert abs(counts["D"] - counts["L"]) / 200 < 0.5


def test_difficulty_changes():
    task = TASK()
    task.config.set_level(0)
    lo = task.config.min_ops
    task.config.set_level(6)
    hi = task.config.max_ops
    assert lo < hi
