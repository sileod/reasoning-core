"""Tests for the knockout_agenda_control task (P001v1)."""

import random

from reasoning_core.tasks.generated.ua_inference_modes_r4.knockout_agenda_control.knockout_agenda_control import (
    IMPOSSIBLE,
    KnockoutAgendaConfig,
    KnockoutAgendaControl,
    _simulate,
    _valid_bracket,
)


def test_generate_score_gold():
    random.seed(7)
    task = KnockoutAgendaControl()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_infeasible_matches_impossible():
    random.seed(11)
    task = KnockoutAgendaControl()
    saw_feasible = False
    saw_infeasible = False
    for _ in range(60):
        ex = task.generate_example()
        if not ex.metadata["feasible"]:
            saw_infeasible = True
            assert ex.answer == IMPOSSIBLE
            assert task.score_answer(IMPOSSIBLE, ex) == 1.0
            assert task.score_answer("R1:1v2;F:1v2", ex) == 0.0
        else:
            saw_feasible = True
            assert ex.answer != IMPOSSIBLE
            assert task.score_answer(IMPOSSIBLE, ex) == 0.0
    assert saw_feasible and saw_infeasible


def test_junk_scores_zero():
    random.seed(3)
    task = KnockoutAgendaControl()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("R1:1v2x;garbage;;", ex) < 1.0
        assert task.score_answer("import fakemodule", ex) < 1.0


def test_levels_change_config():
    random.seed(5)
    task = KnockoutAgendaControl()
    c0 = KnockoutAgendaConfig()
    c0.set_level(0)
    c6 = KnockoutAgendaConfig()
    c6.set_level(6)
    assert c0.n <= c6.n
    assert c0.protected_count <= c6.protected_count


def test_gold_bracket_forces_winner_and_respects_protection():
    random.seed(13)
    task = KnockoutAgendaControl()
    for _ in range(40):
        ex = task.generate_example()
        md = ex.metadata
        if md["feasible"]:
            win = __import__(
                "reasoning_core.tasks.generated.ua_inference_modes_r4"
                ".knockout_agenda_control.knockout_agenda_control",
                fromlist=["_build_win"],
            )._build_win(md["outcomes"])
            assert _valid_bracket(
                ex.answer, md["n"], win, md["winner"], md["protected"]
            )
        else:
            assert ex.answer == IMPOSSIBLE


def test_validate():
    random.seed(2)
    task = KnockoutAgendaControl()
    task.validate(n_samples=6)
