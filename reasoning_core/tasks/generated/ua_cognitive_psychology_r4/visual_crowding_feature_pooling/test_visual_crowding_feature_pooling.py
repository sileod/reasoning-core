import random

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.visual_crowding_feature_pooling.visual_crowding_feature_pooling import (
    FEATURE_SYMBOLS,
    VisualCrowdingFeaturePooling,
)


def test_generate_and_score_all_levels():
    task = VisualCrowdingFeaturePooling()
    for level in range(7):
        cfg = VisualCrowdingFeaturePooling.config_cls()
        cfg.apply_difficulty(level)
        task.config = cfg
        for _ in range(20):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_wrong_answer_scores_zero():
    task = VisualCrowdingFeaturePooling()
    entry = task.generate_example()
    wrong = "nonexistent_symbol"
    assert task.score_answer(wrong, entry) == 0.0
    assert task.score_answer("", entry) == 0.0


def test_target_in_neighborhood():
    task = VisualCrowdingFeaturePooling()
    for level in range(7):
        cfg = VisualCrowdingFeaturePooling.config_cls()
        cfg.apply_difficulty(level)
        task.config = cfg
        entry = task.generate_example()
        assert entry.metadata["target_idx"] in entry.metadata["neighborhood"]
        assert entry.answer in FEATURE_SYMBOLS


def test_label_balance():
    task = VisualCrowdingFeaturePooling()
    for level in range(7):
        cfg = VisualCrowdingFeaturePooling.config_cls()
        cfg.apply_difficulty(level)
        task.config = cfg
        counts = {}
        for _ in range(200):
            entry = task.generate_example()
            counts[entry.answer] = counts.get(entry.answer, 0) + 1
        assert max(counts.values()) < 0.65 * sum(counts.values())
