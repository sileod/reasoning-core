from reasoning_core.tasks.generated.ua_inference_modes_r4.geometric_orientation_entailment.geometric_orientation_entailment import (
    GeometricOrientationEntailment,
    GeoOrientationEntailmentConfig,
    VALID_INFOS,
)


def _make(level):
    cfg = GeoOrientationEntailmentConfig()
    cfg.apply_difficulty(level)
    task = GeometricOrientationEntailment(config_cls=GeoOrientationEntailmentConfig)
    task.config = cfg
    return task, cfg


def test_generates_and_scores_gold():
    for level in range(7):
        task, _ = _make(level)
        for _ in range(40):
            e = task.generate_example()
            assert e.answer in VALID_INFOS
            assert task.score_answer(e.answer, e) == 1.0


def test_junk_and_empty_score_zero():
    task, _ = _make(0)
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("garbage", e) == 0.0
        assert task.score_answer(None, e) == 0.0
        assert task.score_answer("CWX", e) == 0.0


def test_query_not_among_given_facts():
    task, _ = _make(4)
    for _ in range(60):
        e = task.generate_example()
        q = tuple(e.metadata["query"])
        revealed = [tuple(t) for t, s in e.metadata["revealed"]]
        assert q not in revealed


def test_all_levels_generate_and_answer_valid():
    for level in range(7):
        task, _ = _make(level)
        for _ in range(10):
            e = task.generate_example()
            assert e.answer in VALID_INFOS


def test_metadata_json_serializable():
    import json
    task, _ = _make(3)
    for _ in range(10):
        e = task.generate_example()
        json.dumps(dict(e.metadata))


def test_difficulty_changes_config():
    _, c0 = _make(0)
    _, c6 = _make(6)
    assert c0.level == 0 and c6.level == 6


def test_balance_all_labels_present():
    for level in (0, 3, 6):
        task, _ = _make(level)
        seen = set()
        for _ in range(80):
            seen.add(task.generate_example().answer)
        assert len(seen) >= 2
