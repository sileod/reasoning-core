from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.turnpike_distance_reconstruction.turnpike_distance_reconstruction import (
    TurnpikeDistanceReconstruction,
    _reconstruct,
)
from reasoning_core.template import Entry


def _dists(pts):
    return sorted(pts[j] - pts[i] for i in range(len(pts)) for j in range(i + 1, len(pts)))


def test_reconstruct_reproduces_distances():
    pts = sorted([0, 3, 5, 9, 14])
    canon = _reconstruct(_dists(pts))
    assert canon is not None
    assert _dists(canon) == _dists(pts)


def test_reconstruct_is_lexicographically_minimal():
    pts = sorted([0, 3, 5, 9, 14])
    distances = _dists(pts)
    canon = _reconstruct(distances)
    assert canon == sorted(canon)
    assert canon[0] == 0
    assert canon[-1] == max(distances)


def test_level6_survives():
    task = TurnpikeDistanceReconstruction()
    for _ in range(8):
        x = task.generate_example(level=6)
        coords = [int(v) for v in x.answer.split()]
        assert len(coords) >= 10
        assert _dists(coords) == sorted(x.metadata["distances"])


def test_difficulty_changes_config():
    task = TurnpikeDistanceReconstruction()
    task.config.set_level(0)
    n0 = task.config.n_points
    task.config.set_level(6)
    n6 = task.config.n_points
    assert n6 > n0


def test_round_trip_across_levels():
    for level in (0, 2, 5, 6):
        task = TurnpikeDistanceReconstruction()
        x = task.generate_example(level=level)
        assert isinstance(x, Entry)
        assert task.score_answer(x.answer, x) == 1
        coords = [int(v) for v in x.answer.split()]
        assert coords == sorted(coords)
        assert _dists(coords) == sorted(x.metadata["distances"])


def test_score_rejects_garbage():
    task = TurnpikeDistanceReconstruction()
    x = task.generate_example(level=2)
    assert task.score_answer("0 1 2 3", x) == 0
    assert task.score_answer("", x) == 0
    assert task.score_answer("hello world", x) == 0


def test_non_trivial_points():
    task = TurnpikeDistanceReconstruction()
    for _ in range(20):
        x = task.generate_example(level=3)
        coords = [int(v) for v in x.answer.split()]
        assert len(coords) >= 4
        assert coords[0] == 0
