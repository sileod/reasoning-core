import random

from reasoning_core.tasks.generated.wave12.separation_logic_frame.separation_logic_frame import (
    SeparationLogicFrame,
)


def _gold_scored(task, meta):
    entry = EntryProxy(meta)
    return task.score_answer(meta["frame"], entry)


class EntryProxy:
    def __init__(self, meta):
        self.metadata = meta


def test_frames_are_valid_at_levels():
    task = SeparationLogicFrame()
    for level in range(7):
        task.config.set_level(level)
        seen = set()
        for _ in range(40):
            ex = task.generate_example()
            meta = ex.metadata
            locs = list(meta["locs"])
            frame_cells = meta["frame_cells"]
            # frame cells are disjoint from read, and together form the heap minus read
            assert meta["read"] not in frame_cells
            assert sorted(locs) == sorted(frame_cells + [meta["read"]])
            assert _gold_scored(task, meta) == 1.0
            seen.add(ex.answer)
        assert len(seen) > 4


def test_score_rejects_garbage():
    task = SeparationLogicFrame()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("junk", ex) == 0.0
    assert task.score_answer(ex.answer, ex) == 1.0
