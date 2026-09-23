from reasoning_core.tasks.generated.k3_inference_modes_r4.bresenham_raster_trace.bresenham_raster_trace import (
    BresenhamRasterTrace,
    _points_on_line,
    _points_on_circle,
    _line_decisions,
    _format,
)


def _task():
    return BresenhamRasterTrace()


def test_generate_all_modes():
    t = _task()
    seen = set()
    for _ in range(60):
        ex = t.generate_example()
        assert ex.answer == ex.metadata["answer"]
        seen.add(ex.metadata["kind"])
    assert seen == {"line", "circle", "query_pixel", "query_decision"}


def test_line_roundtrip_scores_one():
    t = _task()
    for _ in range(40):
        ex = t.generate_example()
        if ex.metadata["kind"] != "line":
            continue
        pts = _points_on_line(
            ex.metadata["x0"], ex.metadata["y0"],
            ex.metadata["x1"], ex.metadata["y1"],
        )
        assert ex.answer == _format(pts)
        assert ex.metadata["answer"] == _format(pts)
        assert t.score_answer(ex.answer, ex) == 1.0


def test_base_case_single_pixelline():
    assert _points_on_line(0, 0, 0, 0) == [(0, 0)]


def test_diagonal():
    assert _points_on_line(0, 0, 2, 2) == [(0, 0), (1, 1), (2, 2)]


def test_circle_radius():
    pts = _points_on_circle(0, 0, 1)
    assert (1, 0) in pts and (0, 1) in pts and (-1, 0) in pts


def test_all_octants_generated():
    t = _task()
    octants = set()
    for _ in range(150):
        ex = t.generate_example()
        if ex.metadata["kind"] != "line":
            continue
        m = ex.metadata
        dx = m["x1"] - m["x0"]
        dy = m["y1"] - m["y0"]
        octants.add((1 if dx > 0 else -1, 1 if dy > 0 else -1, dx != 0, dy != 0))
    assert len(octants) >= 4


def test_constant_guess_balanced():
    t = _task()
    answers = {}
    for _ in range(300):
        ex = t.generate_example()
        answers[ex.answer] = answers.get(ex.answer, 0) + 1
    max_frac = max(answers.values()) / len(answers)
    assert max_frac < 0.4


def test_score_junk():
    t = _task()
    ex = t.generate_example()
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("garbage", ex) == 0.0


def test_decision_domain():
    t = _task()
    for _ in range(50):
        ex = t.generate_example()
        if ex.metadata["kind"] != "query_decision":
            continue
        assert int(ex.answer) == ex.metadata["decisions"][ex.metadata["q"] - 1]


def test_levels_generate():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(5):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_score_line_orders_matter():
    t = _task()
    for _ in range(100):
        ex = t.generate_example()
        if ex.metadata["kind"] != "line":
            continue
        rev = "".join(reversed(ex.answer.split(")(")))
        assert t.score_answer(rev, ex) == 0.0
