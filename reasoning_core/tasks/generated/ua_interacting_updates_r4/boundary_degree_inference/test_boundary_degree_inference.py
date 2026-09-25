import random

from reasoning_core.template import Entry

from .boundary_degree_inference import (
    BoundaryDegreeInference,
    _winding_angle,
    _winding_ray,
)


def test_generate_and_score_all_levels():
    task = BoundaryDegreeInference()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_garbage_scores_zero():
    task = BoundaryDegreeInference()
    task.config.set_level(4)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0
    assert task.score_answer("12.5", ex) == 0.0


def test_winding_helpers_agree():
    for _ in range(200):
        n = random.randint(4, 20)
        pts = [(random.uniform(-5, 5), random.uniform(-5, 5)) for _ in range(n)]
        if any(abs(x) < 1e-9 and abs(y) < 1e-9 for x, y in pts):
            continue
        assert _winding_angle(pts) == _winding_ray(pts)


def test_answer_domain():
    task = BoundaryDegreeInference()
    task.config.set_level(6)
    i = 0
    values = set()
    while i < 120:
        ex = task.generate_example()
        values.add(ex.answer)
        assert int(ex.answer) == ex.metadata["winding"]
        i += 1
    assert len(values) > 1


def test_metadata_json_roundtrip():
    import json

    task = BoundaryDegreeInference()
    task.config.set_level(3)
    ex = task.generate_example()
    json.dumps(ex.metadata)
    assert isinstance(ex.metadata["boundary"], str)


def test_need_zero_consistent_with_winding():
    task = BoundaryDegreeInference()
    task.config.set_level(5)
    for _ in range(80):
        ex = task.generate_example()
        assert ex.metadata["need_zero"] == (ex.metadata["winding"] != 0)


def test_both_dimensions_appear():
    task = BoundaryDegreeInference()
    task.config.set_level(3)
    dims = set()
    for _ in range(120):
        ex = task.generate_example()
        dims.add(ex.metadata["dim"])
    assert dims == {2, 3}


def test_prompt_tokens_headroom():
    import tiktoken

    enc = tiktoken.get_encoding("cl100k_base")
    task = BoundaryDegreeInference()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert len(enc.encode(ex.prompt)) <= 2048


def test_distractors_are_wrong():
    task = BoundaryDegreeInference()
    task.config.set_level(2)
    ex = task.generate_example()
    for d in task.distractor_candidates(ex):
        assert task.score_answer(d, ex) == 0.0
