from reasoning_core.tasks.game_playing import GameBestMove, GameBestMoveConfig


def test_plain_description_exposes_horizon_payoffs():
    task = GameBestMove(GameBestMoveConfig(horizon=1))
    description = task._plain_description(
        {0: {1}, 1: {2}, 2: set()},
        start=0,
        payoffs={0: 10, 1: 40, 2: 90},
    )

    assert "leaf or the move horizon" in description
    assert "current node's payoff" in description
    assert "Node payoffs: n0:10; n1:40; n2:90" in description
