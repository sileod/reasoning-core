import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sld_resolution import SLDConfig, SLDResolution


def _make_task(level):
    t = SLDResolution()
    t.config.set_level(level)
    return t


def test_generate_and_score_default():
    t = SLDResolution()
    for _ in range(20):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_levels_vary():
    c0 = SLDConfig()
    c0.set_level(0)
    c6 = SLDConfig()
    c6.set_level(6)
    assert c0.n_clauses <= c6.n_clauses
    assert c0.max_answers <= c6.max_answers


def test_metadata_json_serializable():
    t = SLDResolution()
    e = t.generate_example()
    json.dumps(dict(e.metadata))


def test_wrong_answers_fail():
    t = SLDResolution()
    e = t.generate_example()
    assert t.score_answer("garbage", e) == 0.0
    assert t.score_answer("", e) == 0.0


def test_no_constant_answer_profile():
    seen = set()
    t = SLDResolution()
    for _ in range(40):
        e = t.generate_example()
        seen.add(e.answer)
    assert len(seen) > 1


def test_answer_format():
    t = SLDResolution()
    e = t.generate_example()
    assert "unbound" in e.answer or "=" in e.answer
