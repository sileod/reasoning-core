from sympy.geometry import Point

from reasoning_core.tasks.math_geometry import render_text, triangle_position


def test_render_text_replaces_compact_point_refs():
    labels = {"p1": "E", "p2": "F", "p6": "Q"}
    assert render_text("triangle p1p6p2", labels) == "triangle EQF"


def test_triangle_vertex_is_boundary():
    A, B, C = Point(0, 0), Point(2, 0), Point(0, 2)
    assert triangle_position(A, B, C, A) == "boundary"
