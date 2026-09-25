import json

from reasoning_core.tasks.generated.ua_rule_induction_r4.mechanical_backlash_induction.mechanical_backlash_induction import (
    BacklashInductionConfig,
    MechanicalBacklashInduction,
    _final_load,
    _load_track,
)


def test_grid_final_load_matches_track():
    for scene in (1, -1):
        for B in (2, 4, 6, 8):
            for xm in range(B, 30):
                for s0 in range(1, B):
                    for command in range(0, 8):
                        expected = _final_load(B, scene, xm, s0, command)
                        if scene == 1:
                            turn, tend, final = xm, xm - s0, xm - s0 - command
                        else:
                            turn, tend, final = -xm, -xm + s0, -xm + s0 + command
                        traj = [0, turn, tend, final]
                        got = round(_load_track(B, traj))
                        assert got == expected, (
                            (scene, B, xm, s0, command), got, expected)


def test_generate_scores_one_and_survives_json():
    task = MechanicalBacklashInduction()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(40):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            json.dumps(dict(ex.metadata))
            assert isinstance(ex.metadata["final_load"], int)


def test_garbage_scores_zero():
    task = MechanicalBacklashInduction()
    ex = task.generate_example()
    for bad in ("", " ", "reajrjrje9595!", "abc"):
        assert task.score_answer(bad, ex) == 0.0


def test_config_level_changes_difficulty():
    base = BacklashInductionConfig()
    high = BacklashInductionConfig()
    high.set_level(6)
    assert high.x_hi > base.x_hi
    assert high.b_hi > base.b_hi
