import math
import random

import pytest

from reasoning_core.tasks.generated.ua_novel_composition_r5.laminated_section_moments.laminated_section_moments import (
    LaminatedSectionConfig,
    LaminatedSectionMoments,
    _section_quantities,
    compute_answer,
)


def _task_at(level):
    task = LaminatedSectionMoments()
    cfg = LaminatedSectionConfig()
    cfg.set_level(level)
    task.config = cfg
    return task


@pytest.mark.parametrize("level", [0, 1, 2, 3, 4, 5, 6])
def test_generates_valid_instance(level):
    task = _task_at(level)
    random.seed(12345 + level)
    entry = task.generate_entry()
    assert isinstance(entry.answer, str)
    int(entry.answer)
    assert task.score_answer(entry.answer, entry) == 1.0


@pytest.mark.parametrize("level", [0, 3, 6])
def test_answer_matches_recomputation(level):
    task = _task_at(level)
    random.seed(777)
    entry = task.generate_entry()
    assert int(entry.answer) == compute_answer(entry.metadata)


@pytest.mark.parametrize("level", [0, 3, 6])
def test_score_rejects_garbage(level):
    task = _task_at(level)
    random.seed(99)
    entry = task.generate_entry()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("junk", entry) < 1.0
    assert task.score_answer("3.7", entry) < 1.0


@pytest.mark.parametrize("level", [0, 6])
def test_no_constant_answer(level):
    task = _task_at(level)
    random.seed(42)
    answers = set()
    for _ in range(80):
        entry = task.generate_entry()
        answers.add(entry.answer)
    assert len(answers) > 1


def test_difficulty_changes_config():
    task = LaminatedSectionMoments()
    cfg = LaminatedSectionConfig()
    cfg.set_level(0)
    lo = cfg.n_inserts + cfg.n_holes
    cfg.set_level(6)
    hi = cfg.n_inserts + cfg.n_holes
    assert hi > lo


def test_stiffness_weighted_neutral_axis_modality(tmp_path):
    # a single symmetric set: neutral axis must equal stiffness-weighted centroid
    task = _task_at(0)
    random.seed(3)
    for _ in range(40):
        entry = task.generate_entry()
        md = entry.metadata
        rects = [tuple(r) for r in md["rects"]]
        y0, ei = _section_quantities(rects)
        assert abs(md["y0"] - y0) < 1e-9
        assert abs(md["ei"] - ei) < 1e-6
        assert ei > 0


def test_all_modes_appear():
    task = _task_at(6)
    random.seed(11)
    modes = set()
    for _ in range(120):
        entry = task.generate_entry()
        modes.add(entry.metadata["mode"])
    assert modes == {"neutral_axis", "stiffness", "stress_ratio"}
