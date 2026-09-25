import json
import random

from reasoning_core.tasks.generated.ua_language_implementation_r4.antichain_progress_completion.antichain_progress_completion import (
    AntichainProgressCompletion,
    _antichain_incomparable,
    _precedes,
)


def test_roundtrip_all_levels():
    task = AntichainProgressCompletion()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(40):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0
            assert task.score_answer("", entry) < 1.0
            assert task.score_answer("garbage^nonsense", entry) < 1.0
            assert task.score_answer("none", entry) < 1.0


def test_complete_semantics_independent():
    task = AntichainProgressCompletion()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(60):
            entry = task.generate_example()
            m = entry.metadata
            frontier = m["frontier"]
            recomputed = sorted(
                q for q in m["queries"] if not any(_precedes(f, q) for f in frontier)
            )
            assert recomputed == m["complete"]


def test_frontier_is_antichain():
    task = AntichainProgressCompletion()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            entry = task.generate_example()
            f = entry.metadata["frontier"]
            for i in range(len(f)):
                for j in range(i + 1, len(f)):
                    assert _antichain_incomparable(f[i], f[j])


def test_mixture_present():
    task = AntichainProgressCompletion()
    for level in range(7):
        task.config.set_level(level)
        seen_partial = False
        for _ in range(50):
            entry = task.generate_example()
            q = entry.metadata["queries"]
            c = entry.metadata["complete"]
            assert 0 < len(c) < len(q)
            if len(c) < len(q) - 1:
                seen_partial = True
        assert seen_partial


def test_answer_not_surface_readable():
    task = AntichainProgressCompletion()
    task.config.set_level(3)
    variety = set()
    for _ in range(300):
        entry = task.generate_example()
        variety.add(entry.answer)
    assert len(variety) > 30


def test_metadata_json_serializable():
    task = AntichainProgressCompletion()
    for level in (0, 6):
        task.config.set_level(level)
        entry = task.generate_example()
        json.dumps(entry.metadata)


def test_determinism_under_seed():
    random.seed(12345)
    task = AntichainProgressCompletion()
    task.config.set_level(4)
    a = [task.generate_example().answer for _ in range(20)]
    random.seed(12345)
    task = AntichainProgressCompletion()
    task.config.set_level(4)
    b = [task.generate_example().answer for _ in range(20)]
    assert a == b
