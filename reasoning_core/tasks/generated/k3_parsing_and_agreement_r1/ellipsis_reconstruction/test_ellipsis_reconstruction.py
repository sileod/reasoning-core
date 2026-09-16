import importlib

from reasoning_core.template import Entry


def _load():
    return importlib.import_module(
        "reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.ellipsis_reconstruction.ellipsis_reconstruction"
    )


def test_generate_and_score():
    mod = _load()
    task = mod.EllipsisReconstruction()
    for _ in range(200):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("garbage", x) < 1.0


def test_answer_not_on_surface():
    mod = _load()
    task = mod.EllipsisReconstruction()
    for _ in range(400):
        x = task.generate_example()
        p = x.metadata["prompt"]
        a = x.answer
        last_word = p.split()[-1].rstrip(".")
        assert a != last_word
        assert a != p.split()[0]


def test_mode_coverage_and_no_single_label():
    mod = _load()
    task = mod.EllipsisReconstruction()
    seen = set()
    golds = set()
    for _ in range(600):
        x = task.generate_example()
        seen.add(x.metadata["mode"])
        golds.add(x.answer)
    assert len(seen) >= 4
    assert len(golds) >= 20


def test_metadata_json_serializable():
    import json
    mod = _load()
    task = mod.EllipsisReconstruction()
    x = task.generate_example()
    json.dumps(x.metadata)


def test_answer_contains_only_names_and_explicit_resolution():
    mod = _load()
    task = mod.EllipsisReconstruction()
    forbidden = {"he", "she", "him", "her", "himself", "herself"}
    for _ in range(600):
        x = task.generate_example()
        words = set(x.answer.split())
        assert not (words & forbidden)
