import random

from reasoning_core.tasks.generated.k3_interacting_updates_r4.integer_tatonnement_clearing.integer_tatonnement_clearing import (
    IntegerTatonnementClearing,
    demand_sign,
    update_prices,
    simulate,
)


def _task(level):
    cfg = IntegerTatonnementClearing.config_cls()
    cfg.set_level(level)
    t = IntegerTatonnementClearing(config=cfg)
    return t


def test_levels_generate_and_score():
    for level in range(7):
        t = _task(level)
        for _ in range(20):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_garbage_scores_zero():
    for level in (0, 3, 6):
        t = _task(level)
        ex = t.generate_example()
        assert t.score_answer("", ex) < 1.0
        assert t.score_answer("zzz nope", ex) < 1.0


def test_step_answer_is_prices():
    t = _task(3)
    for _ in range(30):
        ex = t.generate_example()
        if ex.metadata["mode"] == "step":
            toks = ex.answer.split()
            assert len(toks) == ex.metadata["n_goods"]
            for x in toks:
                assert int(x) >= 1


def test_update_respects_sign():
    params = [(0, 5, 1, 2), (0, 1, 1, 1)]
    p = (2, 2)
    np_ = update_prices(p, params)
    assert np_[0] == 3
    assert np_[1] == 1


def test_cycle_answer_domain():
    t = _task(5)
    for _ in range(20):
        ex = t.generate_example()
        if ex.metadata["mode"] == "cycle":
            assert ex.answer in ("yes", "no")


def test_deterministic_seed():
    cfg = IntegerTatonnementClearing.config_cls()
    cfg.set_level(3)
    t = IntegerTatonnementClearing(config=cfg)
    random.seed(123)
    a = t.generate_entry()
    random.seed(123)
    b = t.generate_entry()
    assert a.answer == b.answer
