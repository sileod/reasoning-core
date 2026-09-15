import random

from reasoning_core.tasks.generated.k3_incremental_recomputation_r1.skyline_rectangle_update.skyline_rectangle_update import (
    SkylineRectangleUpdate,
    _parse_answer,
    _skyline_rle,
    _total_area,
    _diff_segments,
)


def test_gold_scores_one():
    task = SkylineRectangleUpdate()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = SkylineRectangleUpdate()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer("2-4 x->y ; abc", ex) == 0.0
    assert task.score_answer(None, ex) == 0.0


def test_answer_parseable_and_consistent():
    task = SkylineRectangleUpdate()
    for _ in range(20):
        ex = task.generate_example()
        parsed = _parse_answer(ex.answer)
        assert parsed is not None
        segs, delta = parsed
        md = ex.metadata
        assert [list(s) for s in segs] == md["segments"]
        assert delta == md["area_delta"]


def test_area_delta_domain():
    task = SkylineRectangleUpdate()
    for _ in range(40):
        ex = task.generate_example()
        if ex.metadata["op"] == "insert":
            assert ex.metadata["area_delta"] > 0
        else:
            assert ex.metadata["area_delta"] < 0


def test_segments_within_span():
    task = SkylineRectangleUpdate()
    for _ in range(40):
        ex = task.generate_example()
        l, r, h = ex.metadata["rect"]
        for seg in ex.metadata["segments"]:
            assert seg[0] >= l and seg[1] <= r
            if ex.metadata["op"] == "insert":
                assert seg[3] > seg[2]
            else:
                assert seg[3] < seg[2]


def test_skyline_recomputes_delta():
    task = SkylineRectangleUpdate()
    for _ in range(40):
        ex = task.generate_example()
        base_rects = [tuple(x) for x in ex.metadata["base_rects"]]
        l, r, h = ex.metadata["rect"]
        op = ex.metadata["op"]
        width = ex.metadata["width"]
        if op == "insert":
            new_rects = base_rects + [(l, r, h)]
        else:
            new_rects = [x for x in base_rects if x != (l, r, h)]
        base_runs = _skyline_rle(base_rects, width)
        new_runs = _skyline_rle(new_rects, width)
        segs = _diff_segments(base_runs, new_runs)
        assert [(a, b, c, d) for a, b, c, d in segs] == [
            tuple(s) for s in ex.metadata["segments"]
        ]
        expected_delta = _total_area(new_runs) - _total_area(base_runs)
        assert ex.metadata["area_delta"] == expected_delta


def test_both_ops_and_levels():
    task = SkylineRectangleUpdate()
    ops = set()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            ops.add(ex.metadata["op"])
    assert ops == {"insert", "remove"}


def test_score_rejects_wrong_delta():
    task = SkylineRectangleUpdate()
    ex = task.generate_example()
    parsed = _parse_answer(ex.answer)
    segs, delta = parsed
    wrong = _seg_format(segs) + f" ; {delta + 1}"
    assert task.score_answer(wrong, ex) == 0.0


def _seg_format(segs):
    return ", ".join(f"{a}-{b} {c}->{d}" for a, b, c, d in segs)


def test_reproducible_under_seed():
    random.seed(1475571465)
    a = [SkylineRectangleUpdate().generate_example().answer for _ in range(8)]
    random.seed(1475571465)
    b = [SkylineRectangleUpdate().generate_example().answer for _ in range(8)]
    assert a == b
