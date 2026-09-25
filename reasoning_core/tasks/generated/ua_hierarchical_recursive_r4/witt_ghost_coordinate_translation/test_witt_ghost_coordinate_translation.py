import os
import random

from reasoning_core.tasks.generated.ua_hierarchical_recursive_r4.witt_ghost_coordinate_translation import (
    witt_ghost_coordinate_translation as m,
)


def test_gold_scores_one():
    task = m.WittGhostCoordinateTranslation()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = m.WittGhostCoordinateTranslation()
    ex = task.generate_example()
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("garbage", ex) < 1.0


def test_labels_balanced():
    task = m.WittGhostCoordinateTranslation()
    modes = set()
    families = set()
    past_answers = set()
    for _ in range(60):
        ex = task.generate_example()
        modes.add(ex.metadata["mode"])
        families.add(ex.metadata["family"])
        past_answers.add(ex.answer)
    assert {"to_ghost", "from_ghost", "obstruction"} <= modes
    assert {"p_typical", "big"} <= families
    assert len(past_answers) > 5


def test_recover_roundtrip():
    p = 3
    for _ in range(50):
        a = m._p_coords(5, 4)
        w = m._p_ghosts(p, a)
        rec, fail = m._p_recover(p, w)
        assert fail is None and rec == a
    for _ in range(50):
        a = m._big_coords(5, 4)
        w = m._big_ghosts(a)
        rec, fail = m._big_recover(w)
        assert fail is None and rec == a[1:]


def test_obstruction_first_index():
    p = 3
    for _ in range(50):
        a = m._p_coords(6, 4)
        w = m._p_ghosts(p, a)
        i0 = random.randint(1, 5)
        w[i0] += random.choice([-1, 1])
        rec, fail = m._p_recover(p, w)
        assert fail == i0
    for _ in range(50):
        a = m._big_coords(6, 4)
        w = m._big_ghosts(a)
        i0 = random.randint(2, 6)
        w[i0] += random.choice([-1, 1])
        rec, fail = m._big_recover(w)
        assert fail == i0


def test_answer_recomputable_from_prompt():
    task = m.WittGhostCoordinateTranslation()
    for lvl in (0, 3, 6):
        task.config.set_level(lvl)
        for _ in range(40):
            ex = task.generate_example()
            g = [int(x) for x in ex.metadata["given"].split(",")]
            if ex.metadata["mode"] == "to_ghost":
                if ex.metadata["family"] == "p_typical":
                    assert ex.answer == m._fmt_vec(m._p_ghosts(ex.metadata["p"], g))
                else:
                    assert ex.answer == m._fmt_vec(m._big_ghosts([0] + g)[1:])
                continue
            if ex.metadata["family"] == "p_typical":
                p = ex.metadata["p"]
                rec, fail = m._p_recover(p, g)
                if ex.metadata["mode"] == "from_ghost":
                    assert fail is None
                    assert ex.answer == m._fmt_vec(rec)
                else:
                    assert ex.answer == str(fail + 1)
            else:
                w = [0] + g
                rec, fail = m._big_recover(w)
                if ex.metadata["mode"] == "from_ghost":
                    assert fail is None
                    assert ex.answer == m._fmt_vec(rec)
                else:
                    assert ex.answer == str(fail)


def test_difficulty_changes_config():
    task = m.WittGhostCoordinateTranslation()
    task.config.set_level(0)
    base = task.config.max_len
    task.config.set_level(6)
    assert task.config.max_len > base
