import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from reasoning_core.tasks.generated.k3_counterfactual_r1.delaunay_flip_trace.delaunay_flip_trace import DelaunayFlipTrace


def test_gold_scores_one():
    task = DelaunayFlipTrace()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(5):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_garbage_scores_zero():
    task = DelaunayFlipTrace()
    task.config.set_level(2)
    entry = task.generate_example()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("(0,1)", entry) == 0.0
    assert task.score_answer("garbage", entry) == 0.0


def test_levels_change_config():
    task = DelaunayFlipTrace()
    task.config.set_level(0)
    c0 = task.config.point_count
    task.config.set_level(6)
    c6 = task.config.point_count
    assert c6 > c0


def test_varied_answers():
    task = DelaunayFlipTrace()
    task.config.set_level(0)
    seen = set()
    for _ in range(20):
        entry = task.generate_example()
        seen.add(entry.answer)
    assert len(seen) > 1


def test_nonempty_and_wellformed():
    task = DelaunayFlipTrace()
    for level in (0, 3, 6):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_example()
            assert entry.answer != ""
            seq = entry.metadata["flip_sequence"]
            assert seq
            assert all(e[0] < e[1] for e in seq)
            assert "".join(entry.answer.split()) == entry.answer


def test_answer_not_on_prompt_surface():
    task = DelaunayFlipTrace()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(10):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            assert not prompt.startswith(entry.answer)
            assert not prompt.endswith(entry.answer)
