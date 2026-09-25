import json
import random

from reasoning_core.tasks.generated.ua_uncertainty_r4.residual_symmetry_under_pinning import \
    residual_symmetry_under_pinning as mod


def test_generate_scores_gold():
    task = mod.ResidualSymmetryUnderPinning()
    for _ in range(40):
        ex = task.generate_example()
        assert mod._parse_blocks(ex.answer) == ex.metadata["orbit_blocks"]
        assert task.score_answer(ex.answer, ex) == 1.0


def test_score_rejects_junk_and_wrong():
    task = mod.ResidualSymmetryUnderPinning()
    for _ in range(40):
        ex = task.generate_example()
        for junk in ("", "[[0]", "42", "hello", "[[0,5],[1,2]]"):
            assert task.score_answer(junk, ex) == 0.0


def test_vertex_set_fully_covered():
    task = mod.ResidualSymmetryUnderPinning()
    for _ in range(30):
        ex = task.generate_example()
        m = ex.metadata["m"]
        pinned = ex.metadata["pinned"]
        assert isinstance(m, int) and m >= 4
        assert len(pinned) == len(set(pinned))
        assert all(0 <= p < m for p in pinned)
        flat = [x for b in ex.metadata["orbit_blocks"] for x in b]
        assert sorted(flat) == list(range(m))


def test_difficulty_changes_config():
    task = mod.ResidualSymmetryUnderPinning()
    c0 = task.config.to_dict()
    task.config.set_level(6)
    c6 = task.config.to_dict()
    assert c6["max_vertices"] >= c0["max_vertices"]
    assert c6["max_pinned"] >= c0["max_pinned"]


def test_metadata_json_serializable():
    task = mod.ResidualSymmetryUnderPinning()
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))


def test_dihedral_hand_computed_orbits():
    # Pinned {0} on a hexagon (D_6): residual = {id, reflection through vertex 0}.
    fixed = mod._pointwise_fix(mod._group_elements(6), [0])
    assert len(fixed) == 2
    assert mod._orbits(fixed, 6) == [[0], [1, 5], [2, 4], [3]]
    # No pinned vertices: full dihedral acts transitively on vertices.
    assert mod._orbits(mod._group_elements(6), 6) == [[0, 1, 2, 3, 4, 5]]
    # Pinned {0,3} on a hexagon (antipodal): reflection through the axis through both.
    fixed2 = mod._pointwise_fix(mod._group_elements(6), [0, 3])
    assert len(fixed2) == 2
    assert mod._orbits(fixed2, 6) == [[0], [1, 5], [2, 4], [3]]


def test_reproducible_under_seed():
    random.seed(2409743872)
    a1 = mod.ResidualSymmetryUnderPinning().generate_example().answer
    random.seed(2409743872)
    a2 = mod.ResidualSymmetryUnderPinning().generate_example().answer
    assert a1 == a2


def test_generation_survives_all_levels():
    task = mod.ResidualSymmetryUnderPinning()
    for level in range(0, 7):
        seen = set()
        for _ in range(20):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
        assert len(seen) > 1, f"level {level} produced only one answer: {seen}"


def test_orbit_partition_is_symmetric_closure():
    # Independently re-derive orbits via BFS over the pinned-isotropy subgroup.
    task = mod.ResidualSymmetryUnderPinning()
    for _ in range(30):
        ex = task.generate_example()
        m = ex.metadata["m"]
        pinned = ex.metadata["pinned"]
        fixed = mod._pointwise_fix(mod._group_elements(m), pinned)
        # BFS orbit of each point under the fixed subgroup.
        orbits = []
        unvisited = set(range(m))
        while unvisited:
            start = min(unvisited)
            queue = [start]
            orbit = set()
            while queue:
                v = queue.pop()
                if v in orbit:
                    continue
                orbit.add(v)
                imgs = set()
                for e in fixed:
                    imgs.add(e[v])
                for w in imgs:
                    if w not in orbit:
                        queue.append(w)
            orbits.append(sorted(orbit))
            unvisited -= orbit
        orbits.sort(key=lambda b: b[0])
        assert orbits == ex.metadata["orbit_blocks"]
