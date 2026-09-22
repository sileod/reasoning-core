import pytest

from reasoning_core.tasks.generated.k3_novel_composition_r4.polygon_area_point_location.polygon_area_point_location import (
    LOCATION_LABEL,
    PolygonAreaPointLocation,
    point_classify,
    point_on_edges,
    signed_area,
)


@pytest.fixture
def task():
    return PolygonAreaPointLocation()


def test_doubled_area_nonnegative(task):
    for _ in range(50):
        e = task.generate_example()
        assert isinstance(e.metadata["doubled_area"], int)
        assert e.metadata["doubled_area"] > 0


def test_label_matches_classifier(task):
    for _ in range(50):
        e = task.generate_example()
        assert e.metadata["label"] in LOCATION_LABEL
        assert point_classify(e.metadata["point"], e.metadata["vertices"]) == e.metadata["label"]


def test_answer_format(task):
    for _ in range(50):
        e = task.generate_example()
        area, loc = e.answer.split(" | ")
        assert int(area) == e.metadata["doubled_area"]
        assert loc == LOCATION_LABEL[e.metadata["label"]]


def test_score_gold(task):
    e = task.generate_example()
    assert task.score_answer(e.answer, e) == 1.0


def test_score_junk(task):
    e = task.generate_example()
    assert task.score_answer("junk", e) == 0.0
    assert task.score_answer("", e) == 0.0
    assert task.score_answer(None, e) == 0.0


def test_signed_area_shoelace():
    verts = [(0, 0), (4, 0), (4, 3)]
    assert signed_area(verts) == 12


def test_point_on_edge_detection():
    poly = [(0, 0), (4, 0), (4, 3), (0, 3)]
    assert point_on_edges((2, 0), poly)
    assert not point_on_edges((2, 1), poly)


def test_levels_differ(task):
    base = task.config.__dict__.copy()
    task.config.set_level(3)
    assert task.config.__dict__ != base


def test_boundary_class_found(task):
    labels = set()
    for _ in range(200):
        e = task.generate_example()
        labels.add(e.metadata["label"])
    assert labels == {"inside", "outside", "boundary"}


@pytest.mark.parametrize("level", [0, 6])
def test_generates_all_levels(level):
    t = PolygonAreaPointLocation()
    t.config.set_level(level)
    for _ in range(5):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0
