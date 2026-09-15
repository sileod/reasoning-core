import random

from reasoning_core.tasks.generated.k3_representation_specific_r1.grid_path_count_cone.grid_path_count_cone import (
    GridPathCountCone,
    path_counts,
    MOVE_SETS,
)


def test_round_trip_all_levels():
    task = GridPathCountCone()
    for level in (0, 2, 5, 6):
        random.seed(1234 + level)
        task.config.set_level(level)
        for _ in range(8):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert ex.metadata["corner_after"] >= 0


def test_answer_matches_dp():
    task = GridPathCountCone()
    random.seed(7)
    task.config.set_level(3)
    for _ in range(16):
        ex = task.generate_example()
        m = ex.metadata
        grid2 = [row[:] for row in m["grid"]]
        grid2[m["toggled"][0]][m["toggled"][1]] = m["add_obstacle"]
        move = next(mv for name, mv in MOVE_SETS if name == m["move_set"])
        counts = path_counts(grid2, m["rows"], m["cols"], move)
        assert counts[m["rows"] - 1][m["cols"] - 1] == m["corner_after"]
        gold = ";".join(f"{r},{c}" for r, c in m["changed"]) + f"|{m['corner_after']}"
        assert ex.answer == gold
        assert all(counts[r][c] >= 0 for r in range(m["rows"]) for c in range(m["cols"]))


def test_wrong_answers_do_not_score():
    task = GridPathCountCone()
    random.seed(9)
    for level in (0, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer("", ex) != 1.0
        assert task.score_answer("0,0|0", ex) != 1.0
        assert task.score_answer(ex.answer + "0", ex) != 1.0


def test_knight_count_domain():
    task = GridPathCountCone()
    random.seed(11)
    task.config.set_level(2)
    counts = 0
    for _ in range(60):
        ex = task.generate_example()
        if ex.metadata["move_set"].startswith("knight"):
            counts += 1
    assert counts > 0
    assert task.score_answer(ex.answer, ex) == 1.0


def test_start_corner_never_toggled():
    task = GridPathCountCone()
    for level in (0, 3, 6):
        random.seed(100 + level)
        task.config.set_level(level)
        for _ in range(12):
            ex = task.generate_example()
            tr, tc = ex.metadata["toggled"]
            assert (tr, tc) != (0, 0)
            assert (tr, tc) != (ex.metadata["rows"] - 1, ex.metadata["cols"] - 1)


def test_seeded_determinism():
    task = GridPathCountCone()
    random.seed(42)
    task.config.set_level(3)
    first = task.generate_example().answer
    random.seed(42)
    task.config.set_level(3)
    second = task.generate_example().answer
    assert first == second
