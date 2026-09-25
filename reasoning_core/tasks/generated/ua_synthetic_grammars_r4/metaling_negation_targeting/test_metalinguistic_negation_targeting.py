import random
from pathlib import Path

random.seed(1259343118)


def test_validation():
    from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.metalinguistic_negation_targeting.metalinguistic_negation_targeting import MetalingNegationTargetingV3
    task = MetalingNegationTargetingV3()
    task.validate()


def test_label_balance_across_samples():
    from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.metalinguistic_negation_targeting.metalinguistic_negation_targeting import MetalingNegationTargetingV3
    counts = {}
    for _ in range(200):
        task = MetalingNegationTargetingV3()
        task.config.set_level(random.randrange(7))
        ex = task.generate_example()
        counts[ex.answer] = counts.get(ex.answer, 0) + 1
    assert len(counts) == 4, counts


def test_roundtrip_score():
    from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.metalinguistic_negation_targeting.metalinguistic_negation_targeting import MetalingNegationTargetingV3
    task = MetalingNegationTargetingV3()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("truthfulness", ex) == 0.0


def test_metadata_json_serializable():
    import json
    from reasoning_core.tasks.generated.ua_synthetic_grammars_r4.metalinguistic_negation_targeting.metalinguistic_negation_targeting import MetalingNegationTargetingV3
    task = MetalingNegationTargetingV3()
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        json.dumps(ex.metadata)
