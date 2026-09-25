import random

from reasoning_core.tasks.generated.ua_interacting_updates_r4.periodic_weave_reconstruction.periodic_weave_reconstruction import (
    PeriodicWeaveReconstruction,
    necklace_period,
    min_rotation_index,
    periodic_shift,
)


def test_necklace_period():
    assert necklace_period("ABAB") == 2
    assert necklace_period("AAAA") == 1
    assert necklace_period("ABC") == 3
    assert necklace_period("ABCABC") == 3


def test_min_rotation_index():
    assert min_rotation_index("ABAB") == 0


def test_periodic_shift():
    p, s = periodic_shift("ABAB")
    assert p == 2


def test_generate_and_score():
    task = PeriodicWeaveReconstruction()
    for level in (0, 1, 3, 6):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1
            assert task.score_answer("", x) == 0
            assert task.score_answer("junk", x) == 0
            assert task.score_answer(x.answer + " ", x) == 1


def test_answer_matches_computation():
    task = PeriodicWeaveReconstruction()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            md = x.metadata
            p_row, s_row = periodic_shift(md["row_snippet"])
            p_col, s_col = periodic_shift(md["col_snippet"])
            p_diag, s_diag = periodic_shift(md["diag_snippet"])
            assert x.answer == f"R:{p_row},{s_row} C:{p_col},{s_col} D:{p_diag},{s_diag}"


def test_deterministic():
    random.seed(1)
    a = PeriodicWeaveReconstruction().generate_entry()
    random.seed(1)
    b = PeriodicWeaveReconstruction().generate_entry()
    assert a.answer == b.answer
    assert a.metadata["row_snippet"] == b.metadata["row_snippet"]
