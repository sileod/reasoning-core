import importlib.util
import random
from pathlib import Path

_MODULE = Path(__file__).with_name('ratchet_motion_rectification.py')
_spec = importlib.util.spec_from_file_location('ratchet_mod', _MODULE)
_ratchet = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ratchet)
RatchetMotionRectification = _ratchet.RatchetMotionRectification
_contains = _ratchet._contains
_tuple_to_str = _ratchet._tuple_to_str


def test_contains():
    w = (0, 4, True, True)
    assert _contains(w, 0)
    assert _contains(w, 4)
    assert not _contains(w, -1)
    assert not _contains(w, 5)
    w2 = (0, 4, False, True)
    assert not _contains(w2, 0)
    assert _contains(w2, 1)
    assert _contains(w2, 4)


def test_window_str_roundtrip():
    for w in [(0, 4, True, True), (0, 4, False, True), (0, 4, True, False), (0, 4, False, False)]:
        s = _tuple_to_str(w)
        assert len(s) > 0


def test_all_levels_generate():
    for level in range(7):
        task = RatchetMotionRectification()
        task.config.set_level(level)
        ex = task.generate_example()
        assert ex.answer is not None


def test_score_gold_and_junk():
    task = RatchetMotionRectification()
    task.config.set_level(3)
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0
    assert task.score_answer('', ex) < 1.0
    assert task.score_answer('zzz', ex) < 1.0


def test_deterministic_under_seed():
    random.seed(123)
    a = RatchetMotionRectification().generate_example()
    random.seed(123)
    b = RatchetMotionRectification().generate_example()
    assert a.answer == b.answer
    assert a.metadata['strokes'] == b.metadata['strokes']
