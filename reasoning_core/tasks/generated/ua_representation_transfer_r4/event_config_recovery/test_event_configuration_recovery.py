import random

from reasoning_core.tasks.generated.ua_representation_transfer_r4.event_config_recovery.event_configuration_recovery import (
    EventConfigRecoveryConfig,
    EventConfigRecoveryV3,
)


def test_gold_scores_one():
    random.seed(1)
    task = EventConfigRecoveryV3()
    for _ in range(60):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    random.seed(2)
    task = EventConfigRecoveryV3()
    for _ in range(60):
        x = task.generate_example()
        assert task.score_answer("", x) == 0.0
        assert task.score_answer("garbage", x) == 0.0
        assert task.score_answer(x.answer + ",z", x) == 0.0


def test_both_modes_appear():
    random.seed(3)
    task = EventConfigRecoveryV3()
    modes = set()
    for _ in range(80):
        x = task.generate_example()
        modes.add(x.metadata["mode"])
    assert modes == {"causes", "conflicts"}


def test_causes_answer_is_subset_of_universe():
    random.seed(4)
    task = EventConfigRecoveryV3()
    for _ in range(60):
        x = task.generate_example()
        if x.metadata["mode"] != "causes":
            continue
        uni = set(x.metadata["universe"])
        ans = set(x.answer.replace(",", "").replace(" ", ""))
        assert ans and ans <= uni


def test_conflicts_answer_format():
    random.seed(5)
    task = EventConfigRecoveryV3()
    for _ in range(60):
        x = task.generate_example()
        if x.metadata["mode"] != "conflicts":
            continue
        uni = set(x.metadata["universe"])
        for pair in x.answer.split(","):
            p = pair.strip()
            assert len(p) == 2 and set(p) <= uni and p[0] < p[1]


def test_difficulty_scales():
    cfg = EventConfigRecoveryConfig()
    base = cfg.n_events
    cfg.set_level(6)
    assert cfg.n_events >= base
    assert cfg.n_events > 3


def test_generation_survives_all_levels():
    task = EventConfigRecoveryV3()
    for level in range(7):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
