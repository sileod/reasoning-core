import random

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.surface_seam_composition.surface_seam_composition import (
    SurfaceSeamV1,
    boundary_components,
    generate_structure,
)


def _random_instance(level, seed):
    r = random.Random(seed)
    return generate_structure(level, r)


def test_boundary_none_glued_is_face_count_small():
    # A single triangle with no glue -> every corner is a boundary => actually
    # for a single open polygon the boundary is 1 component (the polygon
    # itself is a disk, boundary = the triangle = 1 loop). glue empty with one
    # face of 3 edges: all 3 edges unglued, tracing gives 1 boundary loop.
    faces = [[0, 1, 2]]
    glue = {}
    assert boundary_components(faces, glue) == 1


def test_two_triangles_glued_full_edge_cylinder():
    # Two triangles glued along all 3 edges pairwise -> forms a sphere-like
    # closed surface with no boundary if orientations match appropriately;
    # but edge pairing here labels in order. With 2 triangles glued as a cycle
    # we actually get a closed surface => 0 boundary. This depends on pairing;
    # check deterministically that answer is stable and >= 0.
    faces = [[0, 1, 2], [0, 1, 2]]
    glue = {}
    for i in range(3):
        glue[(0, i)] = (1, i, 1)
        glue[(1, i)] = (0, i, 1)
    # two triangles glued along the 3 edges (preserving) => closed sphere,
    # boundary components = 0.
    assert boundary_components(faces, glue) == 0


def test_disk_single_square_no_glue():
    faces = [[0, 1, 2, 3]]
    glue = {}
    assert boundary_components(faces, glue) == 1


def test_generate_answer_domain_all_levels():
    task = SurfaceSeamV1()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert int(ex.answer) >= 0
            assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_junk():
    task = SurfaceSeamV1()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("banana", ex) < 1.0
    assert task.score_answer("-5", ex) < 1.0


def test_prompt_contains_seam_info():
    task = SurfaceSeamV1()
    task.config.set_level(2)
    ex = task.generate_example()
    p = task.render_prompt(ex.metadata)
    assert "sewn" in p
    assert "boundary component" in p


def test_not_constant_answer():
    task = SurfaceSeamV1()
    task.config.set_level(0)
    answers = set()
    for _ in range(30):
        answers.add(task.generate_example().answer)
    assert len(answers) > 1
