import pytest

from reasoning_core.tasks.generated.k3_psychometrics_r5.figure_symmetry_audit.figure_symmetry_audit import (
    FigureSymmetryAudit,
    FigureSymmetryAuditConfig,
    _rot_order,
    _symmetry_set,
    _render_figure,
)


def test_generate_example_works():
    task = FigureSymmetryAudit()
    x = task.generate_example()
    assert x.answer
    assert x.metadata['syms'] is not None
    assert task.score_answer(x.answer, x) == 1.0


def test_score_rejects_empty_and_garbage():
    task = FigureSymmetryAudit()
    x = task.generate_example()
    assert task.score_answer('', x) == 0.0
    assert task.score_answer('garbage', x) == 0.0


def test_config_difficulty_changes():
    task = FigureSymmetryAudit()
    l0 = FigureSymmetryAuditConfig().apply_difficulty(0)
    base = FigureSymmetryAuditConfig()
    base.set_level(0)
    task.config = base
    task.config.set_level(2)


def test_rot_order_identity():
    assert _rot_order({(0, 0)}, 1) == 4
    assert _rot_order({(0, 0), (0, 1)}, 2) == 1
    assert _rot_order({(0, 1), (1, 1), (2, 1)}, 3) == 2


def test_render_figure():
    fig = _render_figure({(0, 0)}, 2)
    assert 'X' in fig


def test_symmetry_full_square():
    cells = {(r, c) for r in range(3) for c in range(3)}
    syms = _symmetry_set(cells, 3)
    assert set(syms) == {'H', 'V', 'D1', 'D2'}
    assert _rot_order(cells, 3) == 4


def test_all_levels_generate():
    for level in range(7):
        task = FigureSymmetryAudit()
        cfg = FigureSymmetryAuditConfig()
        cfg.set_level(level)
        task.config = cfg
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
