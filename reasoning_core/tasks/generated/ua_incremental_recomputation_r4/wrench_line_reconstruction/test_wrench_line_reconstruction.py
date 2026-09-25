import random

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.wrench_line_reconstruction import (
    wrench_line_reconstruction as wlr,
)


def _entry(level):
    task = wlr.WrenchLineReconstruction()
    task.config.set_level(level)
    return task.generate_example()


def test_all_levels_generate():
    for lvl in range(0, 7):
        e = _entry(lvl)
        assert isinstance(e.answer, str)
        assert e.metadata["axis"] is not None


def test_gold_scores_one():
    random.seed(1)
    task = wlr.WrenchLineReconstruction()
    for _ in range(40):
        e = task.generate_example()
        p = task.render_prompt(e.metadata)
        assert task.score_answer(e.answer, e) == 1.0
        assert p is not None


def test_pure_couple_token():
    random.seed(2)
    task = wlr.WrenchLineReconstruction()
    saw_couple = False
    for _ in range(200):
        e = task.generate_example()
        if e.metadata["variant"] == "couple":
            saw_couple = True
            assert e.answer == "pure couple | pure couple"
            assert e.metadata["resultant_force"] == [0, 0, 0]
    assert saw_couple


def test_bad_answers_fail():
    random.seed(3)
    task = wlr.WrenchLineReconstruction()
    for _ in range(40):
        e = task.generate_example()
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("junk", e) == 0.0
        assert task.score_answer(None, e) == 0.0


def test_axis_verification_matches_pitch():
    random.seed(4)
    task = wlr.WrenchLineReconstruction()
    for _ in range(40):
        e = task.generate_example()
        if e.metadata["axis"] != "pure couple":
            F = e.metadata["resultant_force"]
            M = e.metadata["moment"]
            FF = wlr._dot(F, F)
            MF = wlr._dot(M, F)
            assert wlr._frac_str(MF, FF) == e.metadata["pitch"]
