import random

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.envy_cycle_fair_allocation.envy_cycle_fair_allocation import (
    EnvyCycleFairAllocation,
    _is_ef1,
    _normalize,
)


def test_round_trip_gold_scores():
    random.seed(0)
    task = EnvyCycleFairAllocation()
    for _ in range(20):
        entry = task.generate_entry()
        assert task.score_answer(entry.answer, entry) == 1.0


def test_difficulty_changes_config():
    task = EnvyCycleFairAllocation()
    base = task.config.n_agents
    task.config.set_level(3)
    assert task.config.n_agents > base


def test_gold_is_ef1_and_initial_differs():
    random.seed(1)
    task = EnvyCycleFairAllocation()
    saw_change = False
    for _ in range(20):
        entry = task.generate_entry()
        md = entry.metadata
        assert _is_ef1(
            md["final_allocation"], md["valuations"], md["n_agents"], md["n_items"]
        )
        if md["initial_allocation"] != md["final_allocation"]:
            saw_change = True
    assert saw_change


def test_junk_scores_zero():
    task = EnvyCycleFairAllocation()
    entry = task.generate_entry()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("garbage text", entry) == 0.0


def test_normalize_handles_variant_spacing():
    assert _normalize("I0:A1  I1:A0") == _normalize("I0:A1 I1:A0")
