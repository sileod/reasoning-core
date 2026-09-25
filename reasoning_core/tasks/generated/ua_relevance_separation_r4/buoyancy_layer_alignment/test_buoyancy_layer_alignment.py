import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from buoyancy_layer_alignment import BuoyancyLayerAlignment


def test_roundtrip_all_levels():
    random.seed(2302342651)
    task = BuoyancyLayerAlignment()
    for level in range(7):
        for _ in range(30):
            entry = task.generate_example(level=level)
            assert entry.answer in {"sinks"} or entry.answer.isdigit()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_junk_scores_zero():
    random.seed(1)
    task = BuoyancyLayerAlignment()
    entry = task.generate_example()
    assert task.score_answer("never_a_real_answer", entry) == 0.0
    assert task.score_answer("", entry) == 0.0


def test_both_answers_present():
    random.seed(2302342651)
    task = BuoyancyLayerAlignment()
    answers = set()
    for level in range(7):
        for _ in range(50):
            answers.add(task.generate_example(level=level).answer)
    assert "sinks" in answers
    assert any(a.isdigit() for a in answers)
