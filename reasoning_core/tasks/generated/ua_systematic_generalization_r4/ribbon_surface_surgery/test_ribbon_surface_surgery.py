import random

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.ribbon_surface_surgery.ribbon_surface_surgery import (
    RibbonSurfaceSurgery,
    _boundary_components,
    _format_answer,
)  # noqa


def _reconstruct_answer(metadata):
    # independent recomputation of boundary + genus from the operation narrative
    # using a fresh simulation seeded from metadata
    from reasoning_core.tasks.generated.ua_systematic_generalization_r4.ribbon_surface_surgery import (
        ribbon_surface_surgery as mod,
    )

    sigma, alpha = mod._replay(metadata)
    inv = mod._invariant(sigma, alpha)
    assert inv is not None, "replayed surface not valid"
    _, _, _, genus = inv
    bd = mod._canonical_boundary(mod._boundary_components(sigma, alpha))
    return bd, genus


def test_gold_scores_one():
    task = RibbonSurfaceSurgery()
    task.config.set_level(1)
    for _ in range(5):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_reconstruction_matches():
    task = RibbonSurfaceSurgery()
    task.config.set_level(3)
    for _ in range(5):
        e = task.generate_example()
        bd, genus = _reconstruct_answer(e.metadata)
        assert list(bd) == list(e.metadata["boundary"])
        assert int(genus) == int(e.metadata["genus"])


def test_junk_scores_zero():
    task = RibbonSurfaceSurgery()
    e = task.generate_example()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("garbage", e) == 0.0


def test_genus_domain():
    task = RibbonSurfaceSurgery()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(3):
            e = task.generate_example()
            g = int(e.metadata["genus"])
            assert g >= 0 and g == int(g)
