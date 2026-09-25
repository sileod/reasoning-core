import random

from reasoning_core.tasks.generated.ua_paraphrase_equivalence_r4.portmanteau_spellout.portmanteau_spellout import (
    PortmanteauSpellout,
    _spellout,
)


def _make(level):
    t = PortmanteauSpellout()
    t.config.set_level(level)
    return t


def test_generation_roundtrip():
    t = _make(0)
    ex = t.generate_example()
    assert ex.answer == _spellout(ex.metadata["table"])
    assert ex.prompt and ex.answer


def test_score_gold():
    for level in (0, 1, 2, 5, 6):
        t = _make(level)
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1


def test_score_junk():
    t = _make(0)
    ex = t.generate_example()
    assert t.score_answer("", ex) < 1
    assert t.score_answer("junkstring", ex) < 1


def test_level_changes_config():
    t = _make(0)
    c0 = t.config.to_dict()
    t.config.set_level(6)
    assert t.config.to_dict() != c0


def test_answers_vary():
    t = _make(5)
    answers = {t.generate_example().answer for _ in range(30)}
    assert len(answers) > 5


def test_prompt_spans_levels():
    for level in (0, 2, 5):
        t = _make(level)
        ex = t.generate_example()
        assert "surface word" in ex.prompt
        assert "precedence" in ex.prompt


def test_all_levels_generate():
    for level in range(7):
        t = _make(level)
        ex = t.generate_example()
        assert ex.answer and ex.prompt
        assert t.score_answer(ex.answer, ex) == 1


def test_high_level_structure():
    t = _make(6)
    seen3 = any(t.generate_example().metadata["table"]["n"] == 3 for _ in range(20))
    assert seen3


def test_balanced_batch_levels():
    for level in (0, 6):
        t = _make(level)
        batch = t.generate_balanced_batch(
            batch_size=32, level=level, deduplication=True, workers=1
        )
        assert len(batch) == 32

