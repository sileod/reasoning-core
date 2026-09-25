import random
import sys
from pathlib import Path

from reasoning_core.template import Entry

sys.path.insert(0, str(Path(__file__).parent))

from mass_count_unit_interpretation import (
    MassCountConfig,
    MassCountUnitInterpretation,
    READINGS,
    _clause_answer,
    _plural,
)


def _task(level=0):
    t = MassCountUnitInterpretation()
    t.config.set_level(level)
    return t


def test_generate_and_score_all_levels():
    random.seed(7)
    for level in range(7):
        t = _task(level)
        ex = t.generate_entry()
        assert isinstance(ex, Entry)
        assert ex.answer
        assert t.score_answer(ex.answer, ex) == 1.0


def test_balanced_readings_at_level0():
    random.seed(11)
    t = _task(0)
    counts = {}
    for _ in range(200):
        ex = t.generate_entry()
        counts[ex.answer] = counts.get(ex.answer, 0) + 1
    assert len(counts) >= 2


def test_answer_format():
    assert _clause_answer("coffee", "substance") == "substance"
    assert _clause_answer("coffee", "portion") == "portion: cup"
    assert _clause_answer("wine", "package") == "package: bottle"
    assert _clause_answer("tea", "kind") == "kind: variety"


def test_json_serializable():
    import json

    random.seed(3)
    for level in (0, 6):
        ex = _task(level).generate_entry()
        json.dumps(dict(ex.metadata))


def test_wrong_answers_score_zero():
    random.seed(5)
    t = _task(0)
    ex = t.generate_entry()
    assert t.score_answer("portion: cup", ex) < 1.0 or ex.answer == "portion: cup"
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("junk", ex) == 0.0


def test_difficulty_changes_config():
    t = _task(0)
    assert t.config.occurrences == 1
    t.config.set_level(6)
    assert t.config.occurrences >= 3


def test_pluralization():
    assert _plural("box") == "boxes"
    assert _plural("variety") == "varieties"
    assert _plural("bottle") == "bottles"
    assert _plural("cup") == "cups"


def test_occurrences_monotonic():
    prev = -1
    for level in range(7):
        t = _task(level)
        assert t.config.occurrences >= prev
        prev = t.config.occurrences
