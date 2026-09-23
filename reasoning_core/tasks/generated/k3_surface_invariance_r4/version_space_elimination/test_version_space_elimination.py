import random

from reasoning_core.tasks.generated.k3_surface_invariance_r4.version_space_elimination.version_space_elimination import (
    VersionSpaceElimination, VersionSpaceConfig, _consistent_boxes, _forced_label,
    _box_covers)


def _balanced_labels(n=120):
    random.seed(7)
    task = VersionSpaceElimination()
    counts = {"positive": 0, "negative": 0, "unknown": 0}
    others = 0
    trials = 0
    while sum(counts.values()) < n and trials < 4000:
        trials += 1
        entry = task.generate_example(level=0)
        if entry.metadata["mode"] == "forced":
            counts[entry.metadata["answer"]] += 1
        else:
            others += 1
    return counts


def test_forced_labels_balanced():
    counts = _balanced_labels(60)
    total = sum(counts.values())
    assert total >= 40, counts
    for v in counts.values():
        assert v <= 0.6 * total, counts


def test_score_roundtrip():
    random.seed(3)
    task = VersionSpaceElimination()
    for level in (0, 2, 5, 6):
        for _ in range(10):
            entry = task.generate_example(level=level)
            assert task.score_answer(entry.answer, entry) == 1.0, (level, entry.metadata)
            assert task.score_answer("", entry) == 0.0
            assert task.score_answer("garbage", entry) == 0.0


def test_version_space_is_single_interval():
    random.seed(11)
    task = VersionSpaceElimination()
    for _ in range(30):
        entry = task.generate_example(level=4)
        cons = _consistent_boxes(entry.metadata["features"],
                                 entry.metadata["positives"],
                                 entry.metadata["negatives"])
        assert entry.metadata["s"] in cons
        assert entry.metadata["g"] in cons
        for b in cons:
            assert _box_covers(b, entry.metadata["s"])


def test_difficulty_changes():
    cfg = VersionSpaceConfig()
    cfg.set_level(6)
    assert cfg.features >= 3
    assert cfg.trail >= 6


def test_forced_label_is_exhaustively_correct():
    random.seed(202)
    task = VersionSpaceElimination()
    for level in (0, 3, 6):
        for _ in range(15):
            entry = task.generate_example(level=level)
            if entry.metadata["mode"] != "forced":
                continue
            cons = _consistent_boxes(entry.metadata["features"],
                                     entry.metadata["positives"],
                                     entry.metadata["negatives"])
            lab = _forced_label(cons, entry.metadata["query"])
            assert lab == entry.metadata["answer"], (level, entry.metadata["query"], lab)
            assert entry.metadata["query"] is not None


def test_boundary_answers_match_single_interval():
    random.seed(303)
    task = VersionSpaceElimination()
    for level in (0, 3, 6):
        for _ in range(15):
            entry = task.generate_example(level=level)
            cons = _consistent_boxes(entry.metadata["features"],
                                     entry.metadata["positives"],
                                     entry.metadata["negatives"])
            # s is the unique minimal consistent box, g the unique maximal
            minima = [b for b in cons if not any(o != b and all(
                __gset(o[i]).issubset(__gset(b[i])) for i in range(len(b))) for o in cons)]
            assert len(minima) == 1
            assert minima[0] == entry.metadata["s"]


def __gset(node):
    from reasoning_core.tasks.generated.k3_surface_invariance_r4.version_space_elimination.version_space_elimination import _group_leafset
    return _group_leafset(node)
