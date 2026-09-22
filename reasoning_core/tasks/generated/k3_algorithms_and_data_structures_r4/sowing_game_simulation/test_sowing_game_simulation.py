import random

from reasoning_core.tasks.generated.k3_algorithms_and_data_structures_r4.sowing_game_simulation.sowing_game_simulation import (
    SowingConfig,
    SowingGameSimulation,
    _play,
    _sow_turn,
)


def _fresh():
    return SowingGameSimulation()


def test_gold_scores_one():
    task = _fresh()
    for level in (0, 2, 5, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1


def test_junk_and_empty_score_zero():
    task = _fresh()
    for _ in range(20):
        ex = task.generate_example()
        for bad in ("", " ", "reajrjrje9595!", "0", "-1"):
            if bad != str(ex.answer):
                assert task.score_answer(bad, ex) == 0


def test_modes_all_covered():
    task = _fresh()
    seen = set()
    for _ in range(60):
        ex = task.generate_example()
        seen.add(ex.metadata["mode"])
    assert seen == {"layout", "captured", "illegal"}


def test_layout_answer_matches_simulation():
    task = _fresh()
    for _ in range(20):
        ex = task.generate_example()
        if ex.metadata["mode"] != "layout":
            continue
        play = _play(ex.metadata["board"], ex.metadata["starts"], ex.metadata["direction"])
        assert play is not None and play["illegal"] is None
        final = ",".join(str(x) for x in play["board"])
        assert _norm(ex.answer) == _norm(final)


def test_captured_answer_matches_simulation():
    task = _fresh()
    for _ in range(20):
        ex = task.generate_example()
        if ex.metadata["mode"] != "captured":
            continue
        play = _play(ex.metadata["board"], ex.metadata["starts"], ex.metadata["direction"])
        assert play is not None and play["captured"] == int(ex.answer)


def test_illegal_is_an_empty_pit_at_its_turn():
    task = _fresh()
    for _ in range(20):
        ex = task.generate_example()
        if ex.metadata["mode"] != "illegal":
            continue
        e = int(ex.answer)
        assert ex.metadata["board"][e] == 0
        assert ex.metadata["starts"][0] == e


def test_captured_nonnegative_and_board_domain():
    task = _fresh()
    for _ in range(30):
        ex = task.generate_example()
        if ex.metadata["mode"] == "captured":
            assert int(ex.answer) >= 1
        for v in ex.metadata["board"]:
            assert v >= 0


def test_difficulty_chain():
    task = _fresh()
    l0 = SowingConfig()
    task.config.set_level(6)
    assert task.config.n_pits >= l0.n_pits
    assert task.config.n_starts >= l0.n_starts


def test_levels_0_and_6_generate():
    task = _fresh()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert ex.prompt
            assert task.score_answer(ex.answer, ex) == 1


def test_validate_passes():
    task = _fresh()
    task.validate(n_samples=5)


def test_all_levels_produce_examples():
    task = _fresh()
    for level in range(7):
        task.config.set_level(level)
        examples = [task.generate_example() for _ in range(10)]
        assert all(task.score_answer(ex.answer, ex) == 1 for ex in examples)


def test_layout_answer_is_valid_board():
    task = _fresh()
    for _ in range(25):
        ex = task.generate_example()
        if ex.metadata["mode"] != "layout":
            continue
        final = [int(x) for x in ex.answer.split(",")]
        assert len(final) == ex.metadata["n_pits"]
        assert all(v >= 0 for v in final)


def _norm(text):
    return "".join(str(text).replace(",", " ").split())
