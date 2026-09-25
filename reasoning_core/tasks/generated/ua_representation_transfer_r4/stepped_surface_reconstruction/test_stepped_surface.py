from reasoning_core.tasks.generated.ua_representation_transfer_r4.stepped_surface_reconstruction.stepped_surface_reconstruction import (
    SteppedSurfaceReconstruction,
    make_plane_partition,
    score_cube,
    score_cross,
    score_height,
    _cross_answer,
)


def test_plane_partition_monotone():
    for _ in range(50):
        h = make_plane_partition(6, 6)
        for i in range(6):
            for j in range(6):
                if i > 0:
                    assert h[i][j] <= h[i - 1][j]
                if j > 0:
                    assert h[i][j] <= h[i][j - 1]
                assert 0 <= h[i][j] <= 6


def test_height_scoring():
    task = SteppedSurfaceReconstruction()
    task.config.set_level(3)
    for _ in range(30):
        e = task.generate_example()
        if e.metadata["query"] != "height":
            continue
        assert score_height(e.answer, e) == 1.0
        assert score_height("gcarbage", e) == 0.0


def test_cube_scoring():
    task = SteppedSurfaceReconstruction()
    task.config.set_level(3)
    seen = set()
    for _ in range(40):
        e = task.generate_example()
        if e.metadata["query"] != "cube":
            continue
        assert score_cube(e.answer, e) == 1.0
        assert score_cube("yes" if e.answer == "no" else "no", e) == 0.0
        assert score_cube("junk", e) == 0.0
        seen.add(e.answer)
    assert seen == {"yes", "no"}


def test_cross_scoring():
    task = SteppedSurfaceReconstruction()
    task.config.set_level(3)
    for _ in range(30):
        e = task.generate_example()
        if e.metadata["query"] != "cross":
            continue
        assert score_cross(e.answer, e) == 1.0
        assert len(e.answer) == len(e.metadata["height"]) * len(e.metadata["height"][0])
        wrong = "X" * len(e.answer)
        if wrong == e.answer:
            wrong = "." * len(e.answer)
        assert score_cross(wrong, e) == 0.0
        assert score_cross("", e) == 0.0
        assert _cross_answer(e.metadata) == e.answer


def test_gold_scores_1_all_levels():
    task = SteppedSurfaceReconstruction()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            e = task.generate_example()
            assert task.score_answer(e.answer, e) == 1.0


def test_switching_query_types_encoded():
    task = SteppedSurfaceReconstruction()
    task.config.set_level(2)
    types = set()
    for _ in range(60):
        e = task.generate_example()
        types.add(e.metadata["query"])
    assert types == {"height", "cube", "cross"}


def test_validate_contract():
    task = SteppedSurfaceReconstruction()
    task.validate(n_samples=5)
