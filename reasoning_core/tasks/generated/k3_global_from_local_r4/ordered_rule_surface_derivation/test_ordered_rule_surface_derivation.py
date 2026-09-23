import random

from reasoning_core.tasks.generated.k3_global_from_local_r4.ordered_rule_surface_derivation import (
    ordered_rule_surface_derivation as mod)

Task = mod.OrderedRuleSurfaceDerivation


def _fresh():
    return Task()


def test_generate_and_score():
    random.seed(12345)
    task = _fresh()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert ex.prompt
        assert ex.metadata["mode"] in ("derive", "reorder")


def test_score_rejects_junk():
    random.seed(7)
    task = _fresh()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("reajrjrje9595!", ex) == 0.0


def test_reorder_answers_balanced_and_correct():
    random.seed(99)
    task = _fresh()
    counts = {"Yes": 0, "No": 0}
    for _ in range(200):
        ex = task.generate_example(level=3)
        if ex.metadata["mode"] != "reorder":
            continue
        assert ex.answer in ("Yes", "No")
        counts[ex.answer] += 1
        r1, r2 = ex.metadata["rules"]
        s1 = mod._derive(ex.metadata["underlying"], [r1, r2])
        s2 = mod._derive(ex.metadata["underlying"], [r2, r1])
        expect = "Yes" if s1 != s2 else "No"
        assert ex.answer == expect
    assert counts["Yes"] > 0 and counts["No"] > 0


def test_derive_answer_is_real_surface():
    random.seed(4242)
    task = _fresh()
    for _ in range(100):
        ex = task.generate_example(level=5)
        if ex.metadata["mode"] != "derive":
            continue
        surface = mod._derive(ex.metadata["underlying"], ex.metadata["rules"])
        assert ex.answer == surface
        assert surface != ex.metadata["underlying"]


def test_difficulty_monotonic():
    task = _fresh()
    lens = []
    for level in range(7):
        task.config.set_level(level)
        lens.append(task.config.string_len_max)
    assert lens == sorted(lens)


def test_metadata_json_roundtrip():
    import json
    random.seed(31337)
    task = _fresh()
    ex = task.generate_example(level=6)
    data = json.dumps(dict(ex.metadata))
    assert isinstance(data, str)
