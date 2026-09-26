import random

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.face_tracing.rotation_system_face_tracing import (
    FaceTracing,
    enumerate_faces,
    sample_rotation,
)


def test_enumerate_faces_identity():
    for _ in range(300):
        n = random.randint(4, 10)
        rot = sample_rotation(n)
        lengths = enumerate_faces(rot)
        total_darts = sum(len(lst) for lst in rot)
        assert sum(lengths) == total_darts
        assert lengths == sorted(lengths)
        assert all(x >= 2 for x in lengths)


def test_simple_triangle():
    rot = [[1, 2], [0, 2], [0, 1]]
    assert enumerate_faces(rot) == [3, 3]


def test_simple_diamond():
    # two triangles sharing edge 0-2
    rot = [[1, 2, 3], [0, 2], [0, 1, 3], [0, 2]]
    assert enumerate_faces(rot) == [3, 3, 4]


def test_single_bridge_edge():
    rot = [[1], [0]]
    assert enumerate_faces(rot) == [2]


def test_generate_and_score_roundtrip():
    t = FaceTracing()
    for _ in range(200):
        t.config.set_level(random.randint(0, 6))
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_score_rejects_junk():
    t = FaceTracing()
    for _ in range(80):
        e = t.generate_example()
        assert t.score_answer("", e) < 1.0
        assert t.score_answer("abc", e) < 1.0
        assert t.score_answer(None, e) < 1.0
        assert t.score_answer(" ".join(str(int(x) + 1) for x in e.answer.split()), e) < 1.0


def test_all_levels_generate():
    t = FaceTracing()
    for level in range(7):
        t.config.set_level(level)
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_answer_not_readable_off_surface():
    t = FaceTracing()
    for _ in range(100):
        e = t.generate_example()
        nums = [str(x) for v in range(e.metadata["n"]) for x in e.metadata["rotation"][v]]
        assert e.answer != " ".join(nums)
        assert e.answer != nums[-1]
        assert e.answer != max(nums, key=int)
