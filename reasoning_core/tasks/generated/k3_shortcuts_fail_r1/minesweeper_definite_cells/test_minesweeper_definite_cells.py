import json
import random

import pytest

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.minesweeper_definite_cells.minesweeper_definite_cells import (
    MinesweeperDefiniteCells,
    _parse_answer,
)


@pytest.fixture
def task():
    return MinesweeperDefiniteCells()


def test_gold_scores_one_across_levels(task):
    random.seed(2024)
    for level in range(7):
        for _ in range(5):
            ex = task.generate_example(level=level)
            assert task.score_answer(ex.answer, ex) == 1.0


def test_metadata_json_roundtrip(task):
    random.seed(7)
    for _ in range(5):
        ex = task.generate_example(level=3)
        dumped = json.dumps(ex.metadata)
        assert dumped
        restored = json.loads(dumped)
        assert "mined" in restored and "safe" in restored


def test_junk_scores_zero(task):
    random.seed(99)
    ex = task.generate_example(level=1)
    for bad in ("", "Mined: None Safe: None", "7", "(0,0)", "Sure", "Mined: () Safe: ()"):
        assert task.score_answer(bad, ex) == 0.0


def test_definite_mined_cells_are_true_mines(task):
    random.seed(5)
    for _ in range(5):
        ex = task.generate_example(level=4)
        hidden = {tuple(c) for c in ex.metadata["hidden"]}
        mined = {tuple(c) for c in ex.metadata["mined"]}
        safe = {tuple(c) for c in ex.metadata["safe"]}
        assert mined <= hidden
        assert safe <= hidden
        assert not (mined & safe)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_parse_handles_none_and_pairs():
    assert _parse_answer("Mined: None Safe: (0,0),(2,1)") == (set(), {(0, 0), (2, 1)})
    assert _parse_answer("Mined: (0,1) Safe: None") == ({(0, 1)}, set())
    assert _parse_answer("junk") is None


def test_levels_0_and_6_headroom(task):
    for level in (0, 6):
        ex = task.generate_example(level=level)
        toks = len(ex.prompt.split())
        assert toks < 2048
