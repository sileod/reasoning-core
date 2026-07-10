from sympy.geometry import Point

from easydict import EasyDict as edict

from reasoning_core.tasks import math_geometry
from reasoning_core.tasks.math_geometry import render, render_text, triangle_position


def test_render_text_replaces_compact_point_refs():
    labels = {"p1": "E", "p2": "F", "p6": "Q"}
    assert render_text("triangle p1p6p2", labels) == "triangle EQF"


def test_triangle_vertex_is_boundary():
    A, B, C = Point(0, 0), Point(2, 0), Point(0, 2)
    assert triangle_position(A, B, C, A) == "boundary"


def test_render_separates_coordinate_and_construction_modes(monkeypatch):
    scene = {
        "points": {"p0": Point(0, 0), "p1": Point(2, 0), "p2": Point(1, 0)},
        "definitions": {"p2": "the midpoint of p0 and p1"},
        "depth": {"p0": 0, "p1": 0, "p2": 1},
    }
    query = edict(
        additions=[],
        kind="choice",
        answer="Yes",
        question="Is point p2 on segment p0p1?",
        instruction="Answer is either Yes or No.",
        type="between",
        balance="between:Yes",
    )
    monkeypatch.setattr(math_geometry.random, "sample", lambda population, count: list(population))

    coordinate = render(scene, query, construction_execution=False)
    construction = render(scene, query, construction_execution=True)

    assert coordinate.points == {"A": "(0, 0)", "B": "(2, 0)", "C": "(1, 0)"}
    assert coordinate.definitions == []
    assert construction.points == {"A": "(0, 0)", "B": "(2, 0)"}
    assert construction.definitions == ["C is the midpoint of A and B."]
