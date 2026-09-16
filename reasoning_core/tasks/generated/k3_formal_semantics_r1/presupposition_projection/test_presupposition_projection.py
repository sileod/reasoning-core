import random

from reasoning_core.template import Config
from reasoning_core.tasks.generated.k3_formal_semantics_r1.presupposition_projection.presupposition_projection import (
    PresuppositionProjection,
)


def test_generate_and_score():
    task = PresuppositionProjection()
    for level in range(7):
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        entry = task.generate_example()
        assert entry.answer in {"YY", "YN", "YYY", "YNN", "YYYY", "YNNN"}
        assert task.score_answer(entry.answer, entry) == 1.0
        assert task.score_answer("", entry) == 0.0
        assert task.score_answer("zz", entry) == 0.0


def test_answer_not_on_surface():
    task = PresuppositionProjection()
    random.seed(7)
    for _ in range(20):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        assert entry.answer not in prompt


def test_difficulty_changes_config():
    task = PresuppositionProjection()
    c0 = task.config_cls()
    c0.set_level(0)
    c6 = task.config_cls()
    c6.set_level(6)
    assert c0.level == 0
    assert c6.level == 6


def test_metadata_json_serializable():
    import json

    task = PresuppositionProjection()
    entry = task.generate_example()
    json.dumps(entry.metadata)
