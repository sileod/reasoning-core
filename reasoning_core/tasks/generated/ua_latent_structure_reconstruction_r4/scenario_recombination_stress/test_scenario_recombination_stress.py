import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from reasoning_core.tasks.generated.ua_latent_structure_reconstruction_r4.scenario_recombination_stress.scenario_recombination_stress import (  # noqa: E402
    ScenarioConfig,
    ScenarioRecombinationStress,
)
Task = ScenarioRecombinationStress


def test_gold_scores_one():
    task = Task()
    task.config = ScenarioConfig()
    for level in (0, 2, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = Task()
    task.config = ScenarioConfig()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage", ex) < 1.0
    assert task.score_answer("-5", ex) < 1.0


def test_answer_nonnegative_int():
    task = Task()
    task.config = ScenarioConfig()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            v = int(ex.answer)
            assert v >= 0


def test_difficulty_changes():
    cfg = ScenarioConfig()
    c0 = ScenarioConfig()
    c0.apply_difficulty(0)
    c6 = ScenarioConfig()
    c6.apply_difficulty(6)
    assert (c6.length, c6.history) != (c0.length, c0.history)


def test_fwd_bwd_sequences_present():
    task = Task()
    task.config = ScenarioConfig()
    task.config.set_level(0)
    ex = task.generate_example()
    assert "fwd_seq" in ex.metadata
    assert "bwd_seq" in ex.metadata
