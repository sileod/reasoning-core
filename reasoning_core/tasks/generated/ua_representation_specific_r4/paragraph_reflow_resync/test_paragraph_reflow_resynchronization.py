import random

from reasoning_core.tasks.generated.ua_representation_specific_r4.paragraph_reflow_resync.paragraph_reflow_resynchronization import (
    ParagraphReflowResync,
    ParagraphReflowResyncConfig,
)

random.seed(1475571465)


def test_gold_answer_scores_one_at_all_levels():
    task = ParagraphReflowResync()
    for level in (0, 2, 5, 6):
        cfg = ParagraphReflowResyncConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(40):
            entry = task.generate_entry()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_matches_independent_layout():
    task = ParagraphReflowResync()
    task.config = ParagraphReflowResyncConfig()
    for _ in range(60):
        entry = task.generate_entry()
        b = entry.metadata["lines_before"]
        a = entry.metadata["lines_after"]
        expected = sorted(i for i in range(max(len(b), len(a)))
                          if (b[i] if i < len(b) else None) != (a[i] if i < len(a) else None))
        if not expected:
            expected = [len(b)]
        parsed = sorted(int(x) for x in eval(entry.answer))
        assert parsed == expected == sorted(entry.metadata["changed"])


def test_answer_format_is_sorted_int_list():
    task = ParagraphReflowResync()
    task.config = ParagraphReflowResyncConfig()
    entry = task.generate_entry()
    parsed = eval(entry.answer)
    assert isinstance(parsed, list)
    assert parsed == sorted(parsed)
    assert all(isinstance(x, int) for x in parsed)


def test_garbage_scores_zero():
    task = ParagraphReflowResync()
    task.config = ParagraphReflowResyncConfig()
    entry = task.generate_entry()
    assert task.score_answer("", entry) == 0.0
    assert task.score_answer("bogus", entry) == 0.0
    assert task.score_answer("42", entry) == 0.0
