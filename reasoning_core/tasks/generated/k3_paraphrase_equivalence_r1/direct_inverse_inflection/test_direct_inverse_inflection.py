import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from direct_inverse_inflection import (
    DirectInverseInflection,
    _ablaut,
    _gold_string,
    _voice,
    _role_for_person,
)


def test_gold_roundtrip():
    task = DirectInverseInflection()
    for _ in range(50):
        e = task.generate_example()
        assert e.answer == _gold_string(e)
        assert task.score_answer(e.answer, e) == 1.0


def test_bad_answers_fail():
    task = DirectInverseInflection()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer("", e) == 0.0
        assert task.score_answer("xyzzy", e) == 0.0


def test_voice_logic():
    # non-third outranks any third -> patient third direct when agent non-third
    agent = _role_for_person("1s")
    patient = _role_for_person("3", "obviative")
    assert _voice(agent, patient)[0] == "direct"
    # third patient with non-third agent is never inverse
    agent2 = _role_for_person("3", "proximate")
    patient2 = _role_for_person("1s")
    assert _voice(agent2, patient2)[0] == "inverse"
    # prox > obv
    assert _voice(_role_for_person("3", "proximate"),
                  _role_for_person("3", "obviative"))[0] == "direct"
    assert _voice(_role_for_person("3", "obviative"),
                  _role_for_person("3", "proximate"))[0] == "inverse"


def test_stem_changes_with_voice():
    # same root/roles differing only in which gets proximate must differ in stem
    direct = _ablaut("kak", False)
    inverse = _ablaut("kak", True)
    assert direct == "kakan"
    assert inverse == "kaakin"
    assert direct != inverse


def test_both_voices_occur():
    random.seed(1)
    task = DirectInverseInflection()
    voices = {task.generate_example().metadata["voice"] for _ in range(200)}
    assert voices == {"direct", "inverse"}


def test_difficulty_changes_config():
    task = DirectInverseInflection()
    base = task.config.third_prob
    task.config.set_level(6)
    assert task.config.third_prob > base


def test_levels_generate():
    task = DirectInverseInflection()
    for level in range(7):
        task.config.set_level(level)
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_metadata_jsonable():
    import json
    task = DirectInverseInflection()
    e = task.generate_example()
    json.dumps(e.metadata)
