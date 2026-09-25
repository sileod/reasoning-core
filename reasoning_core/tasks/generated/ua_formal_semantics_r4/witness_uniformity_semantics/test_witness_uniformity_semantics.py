import random
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "wus_test", HERE / "witness_uniformity_semantics.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_gen_render_score():
    mod = _load()
    random.seed(1)
    task = mod.WitnessUniformitySemantics(config=mod.UniformityConfig())
    for _ in range(30):
        ex = task.generate_example()
        assert ex.answer in ("yes", "no")
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("yes" if ex.answer == "no" else "no", ex) < 1.0
        assert task.score_answer("", ex) < 1.0
        assert len(task.render_prompt(ex.metadata)) > 0


def test_difficulty_changes():
    mod = _load()
    c0 = mod.UniformityConfig()
    c0.set_level(0)
    c6 = mod.UniformityConfig()
    c6.set_level(6)
    assert (c6.nvars, c6.nclauses, c6.domain_size) != (c0.nvars, c0.nclauses, c0.domain_size)


def test_both_labels_present():
    mod = _load()
    random.seed(7)
    task = mod.WitnessUniformitySemantics(config=mod.UniformityConfig())
    labels = set()
    for _ in range(120):
        labels.add(task.generate_example().answer)
    assert labels == {"yes", "no"}


def test_levels_generate():
    mod = _load()
    for level in range(7):
        random.seed(level)
        conf = mod.UniformityConfig()
        conf.set_level(level)
        task = mod.WitnessUniformitySemantics(config=conf)
        ex = task.generate_example()
        assert ex.answer in ("yes", "no")
        assert task.score_answer(ex.answer, ex) == 1.0


def test_metadata_json_serializable():
    import json

    mod = _load()
    random.seed(3)
    task = mod.WitnessUniformitySemantics(config=mod.UniformityConfig())
    ex = task.generate_example()
    json.dumps(ex.metadata)
