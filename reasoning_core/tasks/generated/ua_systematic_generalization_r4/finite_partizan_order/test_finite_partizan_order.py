from reasoning_core.tasks.generated.ua_systematic_generalization_r4.finite_partizan_order.finite_partizan_order import (
    FinitePartizanOrder,
    compare_positions,
    build_game,
    left_wins,
)


def test_gold_roundtrip_all_levels():
    task = FinitePartizanOrder()
    for level in range(7):
        task.config.set_level(level)
        seen = set()
        for _ in range(40):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.answer)
        assert len(seen) > 1


def test_all_four_labels_reachable():
    task = FinitePartizanOrder()
    labels = set()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(120):
            ex = task.generate_example()
            labels.add(ex.answer)
    assert {"less", "equal", "greater", "incomparable"} <= labels


def test_scoring_exact_and_case_insensitive():
    task = FinitePartizanOrder()
    for level in (0, 5):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer.upper(), ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("fuzzy", ex) == 0.0
        assert task.score_answer("  %s  " % ex.answer, ex) == 1.0


def test_comparison_is_symmetric():
    task = FinitePartizanOrder()
    for level in (0, 6):
        task.config.set_level(level)
        for _ in range(60):
            ex = task.generate_example()
            res = compare_positions(
                (ex.metadata["game_a_l"], ex.metadata["game_a_r"]),
                (ex.metadata["game_b_l"], ex.metadata["game_b_r"]),
            )
            # swapping A and B inverts the order (equal stays equal)
            rev = compare_positions(
                (ex.metadata["game_b_l"], ex.metadata["game_b_r"]),
                (ex.metadata["game_a_l"], ex.metadata["game_a_r"]),
            )
            expect = {"less": "greater", "greater": "less"}.get(res, res)
            assert rev == expect


def test_left_wins_memo_terminates():
    g = build_game(6, 0.6)
    memo = {}
    left_wins(((0, 5, 1), (1, 5, -1)), "L", memo, {0: g[0], 1: g[0]}, {0: g[1], 1: g[1]})
    assert len(memo) >= 1
