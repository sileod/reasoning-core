import itertools
import json
import random
from collections import Counter

import pytest

from reasoning_core.tasks.generated.k3_psychometrics_r1.block_pile_surface_accounting import block_pile_surface_accounting as mod


def _face_profile(cells):
    faces = Counter()
    per_cube = []
    for x, y, z in sorted(cells):
        cube_faces = [(0, x, y, z), (0, x + 1, y, z),
                      (1, y, x, z), (1, y + 1, x, z),
                      (2, z, x, y), (2, z + 1, x, y)]
        faces.update(cube_faces)
        per_cube.append(cube_faces)
    counts = [0] * 6
    for cube_faces in per_cube:
        k = sum(faces[f] == 1 and not (f[0] == 2 and f[1] == 0) for f in cube_faces)
        counts[k] += 1
    return counts


@pytest.mark.parametrize("heights,expected", [
    ([[1]], [0, 0, 0, 0, 0, 1]),
    ([[1, 1]], [0, 0, 0, 0, 2, 0]),
    ([[1, 1], [1, 1]], [0, 0, 0, 4, 0, 0]),
    ([[2, 1], [1, 1]], [0, 0, 1, 3, 0, 1]),
    ([[2]], [0, 0, 0, 0, 1, 1]),
    ([[3] * 3 for _ in range(3)], [2, 9, 12, 4, 0, 0]),
    ([[1, 0], [0, 1]], [0, 0, 0, 0, 0, 2]),
    ([[2, 0, 2]], [0, 0, 0, 0, 2, 2]),
])
def test_known_shapes(heights, expected):
    cells = mod._occupied_cells(heights)
    assert mod._exposure_counts(cells) == expected
    assert mod._column_profile(heights) == expected
    assert _face_profile(cells) == expected


def test_exhaustive_small_height_maps():
    for flat in itertools.product(range(4), repeat=6):
        heights = [flat[:3], flat[3:]]
        cells = mod._occupied_cells(heights)
        assert mod._exposure_counts(cells) == mod._column_profile(heights) == _face_profile(cells)


def test_floating_cube_rejected():
    with pytest.raises(AssertionError):
        mod._exposure_counts({(0, 0, 1)})


def test_generated_invariants_and_distribution():
    state = random.getstate()
    random.seed(177)
    try:
        for level in range(7):
            task = mod.BlockPileSurfaceAccounting()
            task.config.set_level(level)
            answers, representations, floors = set(), set(), set()
            for _ in range(35):
                entry = task.generate_example()
                metadata = json.loads(json.dumps(entry.metadata))
                counts = list(map(int, entry.answer.split(",")))
                cells = {tuple(p) for p in metadata["coordinates"]}
                assert cells == mod._occupied_cells(metadata["heights"])
                assert counts == _face_profile(cells)
                assert sum(counts) == metadata["num_cubes"]
                assert task.score_answer(entry.answer, entry) == 1.0
                assert task.render_prompt(metadata) == task.render_prompt(entry.metadata)
                assert metadata["_prompt_tokens"] <= 2048
                answers.add(entry.answer)
                representations.add(metadata["representation"])
                floors.add(metadata["floor"])
            assert len(answers) >= 5
            assert representations == {"coordinates", "heights"}
            assert floors == {"bounded", "open"}
    finally:
        random.setstate(state)


def test_scorer_is_stateless_and_rejects_malformed_answers():
    class NoAccess:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = mod.Entry(metadata={}, answer="1,2,3,4,5,6")
    score = mod.BlockPileSurfaceAccounting.score_answer
    assert score(NoAccess(), entry.answer, entry) == 1.0
    assert score(NoAccess(), " 1, 2,3,4,5,6 ", entry) == 1.0
    for answer in ("", "junk", "1,2,3", "6,5,4,3,2,1", "1,2,3,4,5,7",
                   "-1,2,3,4,5,6", "1,2,3,4,5,6,", "1,,2,3,4,5,6",
                   "1.0,2,3,4,5,6", "[1,2,3,4,5,6]", None, [], {}):
        assert score(NoAccess(), answer, entry) == 0.0


def test_prompt_explicit_floor_and_representation():
    task = mod.BlockPileSurfaceAccounting()
    entry = task.generate_entry()
    for floor, representation in itertools.product(("bounded", "open"), ("heights", "coordinates")):
        metadata = dict(entry.metadata, floor=floor, representation=representation)
        prompt = task.render_prompt(metadata)
        assert "z=0" in prompt
        assert "no walls" in prompt
        assert "no cubes other than those specified" in prompt
        assert "0,0,0,0,0,1" in prompt
        assert "neighbour counting" in prompt
        assert "height map" in prompt if representation == "heights" else "(x, y, z)" in prompt


def test_seeded_generation_and_difficulty_are_reproducible():
    state = random.getstate()
    try:
        runs = []
        for _ in range(2):
            random.seed(1336314872)
            records = []
            for level in range(7):
                task = mod.BlockPileSurfaceAccounting()
                task.config.set_level(level)
                for _ in range(4):
                    entry = task.generate_entry()
                    records.append((task.render_prompt(entry.metadata), entry.answer))
            runs.append(records)
        assert runs[0] == runs[1]
    finally:
        random.setstate(state)


def test_symmetry_preserves_profile():
    heights = [[2, 0, 3], [1, 4, 2]]
    expected = mod._column_profile(heights)
    for transformed in (heights[::-1], [row[::-1] for row in heights], list(zip(*heights))):
        assert mod._column_profile(transformed) == expected
        assert mod._exposure_counts(mod._occupied_cells(transformed)) == expected


def test_generation_verifier_detects_incorrect_gold(monkeypatch):
    monkeypatch.setattr(mod, "_exposure_counts", lambda cells: [len(cells), 0, 0, 0, 0, 0])
    with pytest.raises(AssertionError):
        mod.BlockPileSurfaceAccounting().generate_entry()
