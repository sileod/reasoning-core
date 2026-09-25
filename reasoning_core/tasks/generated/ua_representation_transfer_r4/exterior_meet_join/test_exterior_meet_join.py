import random

from reasoning_core.tasks.generated.ua_representation_transfer_r4.exterior_meet_join.exterior_meet_join import (
    EMPTY, ExteriorMeetJoin, ExteriorMeetJoinV2Config, canonical_point,
    meet_line_line_2d, meet_line_plane_3d, meet_point_line_2d,
)


def test_generate_and_score():
    t = ExteriorMeetJoin()
    for _ in range(50):
        e = t.generate_example()
        assert isinstance(e.answer, str)
        assert t.score_answer(e.answer, e) == 1.0


def test_score_rejects_junk():
    t = ExteriorMeetJoin()
    for _ in range(10):
        e = t.generate_example()
        assert t.score_answer("", e) < 1.0
        assert t.score_answer("garbage", e) < 1.0


def test_balanced_empty():
    t = ExteriorMeetJoin()
    empties = 0
    total = 0
    for _ in range(200):
        e = t.generate_entry()
        total += 1
        if e.answer == EMPTY:
            empties += 1
    assert empties < 0.5 * total


def test_level_scopes_all_supported():
    t = ExteriorMeetJoin()
    for lv in range(7):
        t.config.set_level(lv)
        for _ in range(20):
            e = t.generate_entry()
            assert t.score_answer(e.answer, e) == 1.0


def test_all_levels_have_both_labels():
    for lv in (0, 1, 2, 3, 4, 5, 6):
        t = ExteriorMeetJoin()
        t.config.set_level(lv)
        labels = {t.generate_entry().answer == EMPTY for _ in range(400)}
        assert True in labels and False in labels, f"level {lv} has only {labels}"


def test_error_terms():
    a = (1, 0, 0)
    b = (0, 1, 0)
    assert meet_point_line_2d((1, 1, 0), a, b) == canonical_point((1, 1, 0))
    assert meet_point_line_2d((1, 1, 1), a, b) == EMPTY


def test_modes_present():
    t = ExteriorMeetJoin()
    modes = set()
    for _ in range(300):
        e = t.generate_entry()
        modes.add(e.metadata["mode"])
    assert modes == {"point_line_2d", "line_line_2d", "line_plane_3d"}


def test_difficulty_changes_config():
    t = ExteriorMeetJoin()
    t.config.set_level(6)
    assert t.config.coord_range > ExteriorMeetJoinV2Config().coord_range


def _parse_point(s):
    s = s.strip().strip("()")
    return tuple(int(x) for x in s.split(","))


def test_meet_lies_on_both_blades():
    from reasoning_core.tasks.generated.ua_representation_transfer_r4.exterior_meet_join.exterior_meet_join import (
        cross3, det3,
    )
    t = ExteriorMeetJoin()
    for lv in (0, 1, 3, 6):
        t.config.set_level(lv)
        for _ in range(200):
            e = t.generate_entry()
            m = e.metadata
            if m["mode"] == "point_line_2d":
                if e.answer == EMPTY:
                    assert det3((m["point"],) + m["line"]) != 0
                else:
                    assert det3((m["point"],) + m["line"]) == 0
                    assert e.answer == canonical_point(m["point"])
            elif m["mode"] == "line_line_2d":
                (a, b), (c, d) = m["lines"]
                pt = _parse_point(e.answer)
                assert _on_line_2d(pt, a, b)
                assert _on_line_2d(pt, c, d)
            else:
                (a, b), (c, d, p3) = m["line"], m["plane"]
                pt = _parse_point(e.answer)
                assert _on_line_2d(pt, a, b)
                assert _plane_contains(pt, c, d, p3)


def _linearly_dependent(vs):
    import math
    m = [list(v) for v in vs]
    if not m:
        return True
    nrows = len(m)
    ncols = len(m[0])
    row = 0
    for col in range(ncols):
        piv = None
        for r in range(row, nrows):
            if m[r][col] != 0:
                piv = r
                break
        if piv is None:
            continue
        m[row], m[piv] = m[piv], m[row]
        for r in range(nrows):
            if r != row and m[r][col] != 0:
                g = math.gcd(abs(m[r][col]), abs(m[row][col]))
                g = max(1, g)
                fa = m[r][col] // g
                fb = m[row][col] // g
                for c in range(col, ncols):
                    m[r][c] = m[r][c] * fb - m[row][c] * fa
        row += 1
    return row < len(vs)


def _on_line_2d(pt, a, b):
    return _linearly_dependent([pt, a, b])


def _plane_contains(pt, c, d, e):
    from reasoning_core.tasks.generated.ua_representation_transfer_r4.exterior_meet_join.exterior_meet_join import (
        _plane_normal,
    )
    pi = _plane_normal(c, d, e)
    return sum(x * y for x, y in zip(pi, pt)) == 0
