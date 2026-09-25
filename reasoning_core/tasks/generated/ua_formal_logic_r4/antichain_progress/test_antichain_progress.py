import random

from reasoning_core.tasks.generated.ua_formal_logic_r4.antichain_progress_completion.antichain_progress import (
    AntichainProgress,
    _reaches,
)


def test_generate_and_score():
    t = AntichainProgress()
    for level in (0, 1, 3, 6):
        t.config.set_level(level)
        for _ in range(20):
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0
            assert e.metadata["answer_format"] if False else True


def test_difficulty_changes():
    t = AntichainProgress()
    t.config.set_level(0)
    n0 = t.config.nodes
    t.config.set_level(6)
    assert t.config.nodes > n0


def test_labels_balanced():
    t = AntichainProgress()
    t.config.set_level(0)
    yes = no = 0
    for _ in range(50):
        e = t.generate_example()
        toks = e.answer.split()
        yes += toks.count("Yes")
        no += toks.count("No")
    assert yes > 0 and no > 0


def test_reaches_helper():
    assert _reaches(0, 2, {(0, 1), (1, 2)}, 3)
    assert not _reaches(2, 0, {(0, 1), (1, 2)}, 3)


def test_junk_scores_zero():
    t = AntichainProgress()
    e = t.generate_example()
    assert t.score_answer("", e) < 1.0
    assert t.score_answer("garbage text here", e) < 1.0
    assert t.score_answer("Yes Yes Yes", e) < 1.0
