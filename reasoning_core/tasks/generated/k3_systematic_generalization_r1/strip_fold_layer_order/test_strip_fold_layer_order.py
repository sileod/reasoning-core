import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from strip_fold_layer_order import StripFoldLayerOrder, StripFoldConfig


def test_generate_example():
    random.seed(1)
    task = StripFoldLayerOrder()
    task.config.set_level(0)
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_answers_match_format():
    random.seed(2)
    task = StripFoldLayerOrder()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            x = task.generate_example()
            assert x.answer
            parts = x.answer.split(",")
            assert all(p.strip().isdigit() for p in parts)
            assert len(parts) == task.config.segments


def test_wrong_and_empty_score_zero():
    random.seed(3)
    task = StripFoldLayerOrder()
    task.config.set_level(2)
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("garbage", x) == 0.0
    assert task.score_answer("1", x) == 0.0


def test_difficulty_scales():
    task = StripFoldLayerOrder()
    task.config.set_level(0)
    n0 = task.config.segments
    task.config.set_level(6)
    n6 = task.config.segments
    assert n6 >= n0


def test_varied_answers():
    random.seed(7)
    task = StripFoldLayerOrder()
    task.config.set_level(3)
    answers = set()
    for _ in range(50):
        answers.add(task.generate_example().answer)
    assert len(answers) > 10


def test_label_conservation_every_level():
    random.seed(11)
    task = StripFoldLayerOrder()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            x = task.generate_example()
            segs = [int(p) for p in x.answer.split(",")]
            assert sorted(segs) == sorted(x.metadata["labels"])
            assert len(segs) == len(x.metadata["labels"])
            assert len(set(segs)) == len(segs)
