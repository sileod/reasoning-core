from reasoning_core.tasks.tracking import ReferenceTracking


def test_swap_moves_exchange_single_occupants():
    placement = {"b1": "x1", "b2": "x2", "b3": "x3"}

    moves, resolved = ReferenceTracking()._do_moves(
        placement, list(placement), ["x1", "x2", "x3"],
        n_steps=1, bulk_p=0.0, pronoun_p=0.0, swap_p=1.0,
    )

    assert moves == resolved
    assert moves[0].startswith("Swap the balls in ")
    assert sorted(placement.values()) == ["x1", "x2", "x3"]
    assert placement != {"b1": "x1", "b2": "x2", "b3": "x3"}
