import random

from .conservative_mesh_remapping import ConservativeMeshRemapping


def _gold_via_overlap(entry):
    old_d = entry.metadata["old_density"]
    old_e = entry.metadata["old_edges"]
    ns, ne = entry.metadata["new_cells"][entry.metadata["query"]]
    total = 0.0
    for i in range(len(old_d)):
        ov = max(0, min(ne, old_e[i + 1]) - max(ns, old_e[i]))
        total += ov * old_d[i]
    return total


def test_roundtrip_scoring():
    random.seed(1)
    t = ConservativeMeshRemapping()
    t.config.set_level(3)
    for _ in range(50):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0
        assert abs(float(e.answer) - _gold_via_overlap(e)) < 1e-9


def test_junk_fails():
    random.seed(2)
    t = ConservativeMeshRemapping()
    for _ in range(5):
        e = t.generate_example()
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("not a number", e) == 0.0


def test_all_levels_generate_and_mass_nonneg():
    t = ConservativeMeshRemapping()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(20):
            e = t.generate_example()
            assert float(e.answer) >= 0.0


def test_regression_precision():
    random.seed(5)
    t = ConservativeMeshRemapping()
    e = t.generate_example()
    v = float(e.answer)
    assert t.score_answer(repr(v + 1e-7), e) == 1.0
    assert t.score_answer(repr(v + 0.01), e) == 0.0
