import random

from reasoning_core.tasks.generated.ua_relational_structures_r4.nested_membrane_evolution.nested_membrane_evolution import (  # noqa: E402
    NestedMembraneEvolution,
    NestedMembraneEvolutionConfig,
    _parse_list,
)


def test_gold_score_round_trip():
    random.seed(42)
    task = NestedMembraneEvolution()
    for level in (0, 3, 6):
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex["answer"], ex) == 1.0


def test_bad_answers_score_zero():
    random.seed(7)
    task = NestedMembraneEvolution()
    for level in (0, 3, 6):
        for _ in range(10):
            ex = task.generate_example(level=level)
            assert task.score_answer("", ex) == 0.0
            assert task.score_answer("garbage", ex) == 0.0


def test_parse_list():
    assert _parse_list("[1, 2, 3]") == [1, 2, 3]
    assert _parse_list("[]") == []
    assert _parse_list("[0]") == [0]


def test_determinism_same_seed():
    random.seed(99)
    ex1 = NestedMembraneEvolution().generate_example(level=3)
    random.seed(99)
    ex2 = NestedMembraneEvolution().generate_example(level=3)
    assert ex1["answer"] == ex2["answer"]
    assert ex1["metadata"]["result"] == ex2["metadata"]["result"]


def test_answer_equals_metadata_result():
    random.seed(123)
    task = NestedMembraneEvolution()
    for _ in range(20):
        ex = task.generate_example(level=4)
        assert ex["metadata"]["result"] == _parse_list(ex["answer"])


def test_result_domain():
    random.seed(5)
    task = NestedMembraneEvolution()
    for level in (0, 6):
        for _ in range(20):
            ex = task.generate_example(level=level)
            res = ex["metadata"]["result"]
            for v in res:
                assert v >= 0


def test_config_difficulty_monotonic():
    cfg = NestedMembraneEvolutionConfig()
    cfg.set_level(0)
    base_n = cfg.n_compartments
    cfg.set_level(6)
    assert cfg.n_compartments >= base_n
    assert cfg.max_rounds >= NestedMembraneEvolutionConfig().max_rounds


def test_json_serializable_metadata():
    import json

    random.seed(11)
    task = NestedMembraneEvolution()
    for level in (0, 6):
        ex = task.generate_example(level=level)
        json.dumps(dict(ex["metadata"]))
        json.dumps(ex["answer"])


def test_render_round_trip_consistency():
    random.seed(13)
    task = NestedMembraneEvolution()
    for _ in range(10):
        ex = task.generate_example(level=5)
        rendered = task.render_prompt(ex["metadata"])
        assert rendered == ex["prompt"]
