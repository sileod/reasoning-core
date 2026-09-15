import random

from reasoning_core.tasks.generated.k3_dependence_relevance_r1.ear_clipping_triangulation.ear_clipping_triangulation import (
    EarClippingTriangulation,
    _clip,
    _cross,
    _diag_valid_current,
    _is_simple,
)


def test_task_smoke():
    random.seed(1)
    task = EarClippingTriangulation()
    ex = task.generate_example()
    assert ex.answer.startswith("tips=[")
    assert task.score_answer(ex.answer, ex) == 1.0


def test_clip_validity():
    random.seed(2)
    task = EarClippingTriangulation()
    for _ in range(30):
        ex = task.generate_entry()
        tips = ex.metadata["tips"]
        diags = ex.metadata["diags"]
        n = len(ex.metadata["vertices"])
        assert len(tips) == n - 3
        assert len(diags) == n - 3
        assert len(set(tips)) == len(tips)
        remaining = set(range(n)) - set(tips)
        assert set(ex.metadata["final"]) == remaining
        for (a, c) in diags:
            assert 0 <= a < c < n


def test_first_ear_rule():
    random.seed(3)
    task = EarClippingTriangulation()
    ex = task.generate_example()
    poly = [tuple(v) for v in ex.metadata["vertices"]]
    out = _clip(poly)
    assert out is not None
    tips, diags, final = out
    assert [int(t) for t in tips] == ex.metadata["tips"]
    assert [[int(a), int(c)] for (a, c) in diags] == ex.metadata["diags"]


def test_every_level_generates():
    task = EarClippingTriangulation()
    for level in range(7):
        ex = task.generate_example(level=level)
        assert ex.metadata["_level"] == level
        assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_changes_config():
    task = EarClippingTriangulation()
    c0 = task.config.min_vert
    task.config.set_level(5)
    assert task.config.min_vert > c0


def test_wrong_answers_fail():
    random.seed(5)
    task = EarClippingTriangulation()
    ex = task.generate_example()
    assert task.score_answer("tips=[] diags=[]", ex) < 1.0
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("tips=[0] diags=[(0,1)]", ex) < 1.0
