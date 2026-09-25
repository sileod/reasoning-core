import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.composed_lens_update.composed_lens_update import (  # noqa: E402
    ComposedLensUpdate,
)


def test_generates_and_scores_gold():
    random.seed(1)
    task = ComposedLensUpdate()
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_all_answers_score_gold():
    random.seed(7)
    task = ComposedLensUpdate()
    for _ in range(200):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_rejected_reachable():
    random.seed(7)
    task = ComposedLensUpdate()
    for _ in range(3000):
        task.config.set_level(0)
        ex = task.generate_example()
        if ex.answer == "rejected":
            assert task.score_answer(ex.answer, ex) == 1.0
            return
    raise AssertionError("rejected answer never generated at level 0")


def test_difficulty_changes():
    task = ComposedLensUpdate()
    c0 = ComposedLensUpdate().config.__class__()
    c6 = ComposedLensUpdate().config.__class__()
    ComposedLensUpdate().config.set_level(0)
    base = ComposedLensUpdate().config.n_source
    config = ComposedLensUpdate().config.__class__()
    config.set_level(6)
    assert config.n_source > base
