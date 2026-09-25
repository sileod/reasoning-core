import random
from fractions import Fraction

from reasoning_core.tasks.generated.ua_representation_transfer_r4.plucker_chart_transfer.plucker_chart_transfer import (
    PluckerChartTransfer,
    _labels,
    _plucker_coords,
)

random.seed(1234)


def _make():
    return PluckerChartTransfer()


def test_generate_and_score():
    task = _make()
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1.0


def test_all_levels_generate():
    task = _make()
    for level in range(7):
        entry = task.generate_example(level=level)
        assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_matches_minor_ratio():
    task = _make()
    for level in range(7):
        entry = task.generate_example(level=level)
        md = entry.metadata
        dim, ambient = md["dim"], md["ambient"]
        labels = _labels(dim, ambient)
        coords = _plucker_coords(md["matrix"], dim, labels)
        base_i = labels.index(tuple(md["base_pivot"]))
        target_i = labels.index(tuple(md["target_pivot"]))
        expected = Fraction(coords[target_i], coords[base_i])
        assert Fraction(entry.answer) == expected


def test_junk_scores_zero():
    task = _make()
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("not a number", entry) == 0.0


def test_prompt_contains_required_pieces():
    task = _make()
    entry = task.generate_example()
    p = task.render_prompt(entry.metadata)
    md = entry.metadata
    assert f"k={md['dim']}" in p
    assert f"n={md['ambient']}" in p
    assert "spanning matrix M = [" in p
