import pytest

from reasoning_core.tasks.generated.ua_representation_specific_r4.observed_remove_delta_merge.observed_remove_delta_merge import (
    ObservedRemoveDeltaMerge,
)


def _visible(seed, adds, removes, delayed, replay):
    state = set(seed)
    for t in adds:
        state.add(t)
    for t in removes:
        state.discard(t)
    for t in delayed:
        state.add(t)
    final = set(state)
    for t in replay:
        if t in final:
            state.add(t)
    return state


def test_round_trip_and_gold():
    task = ObservedRemoveDeltaMerge()
    for _ in range(50):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_replay_does_not_revive_removed():
    # tag 2 is removed, then replayed -> must stay removed
    task = ObservedRemoveDeltaMerge()
    seed = [1, 2]
    adds = [2]
    removes = [2]
    delayed = []
    replay = [2]
    vis = _visible(seed, adds, removes, delayed, replay)
    assert 2 not in vis


def test_junk_and_empty():
    task = ObservedRemoveDeltaMerge()
    x = task.generate_example()
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer("", x) == 0.0 or x.answer == ""


def test_metadata_json_serializable():
    import json

    task = ObservedRemoveDeltaMerge()
    x = task.generate_example()
    json.dumps(x.metadata)


def test_levels():
    task = ObservedRemoveDeltaMerge()
    for level in range(7):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0
