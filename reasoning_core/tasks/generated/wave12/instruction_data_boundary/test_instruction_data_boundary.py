import random

from reasoning_core.tasks.generated.wave12.instruction_data_boundary.instruction_data_boundary import (
    BoundaryConfig,
    InstructionDataBoundary,
)


def test_generate_example_works():
    random.seed(1356906099)
    task = InstructionDataBoundary()
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_difficulty_changes():
    task = InstructionDataBoundary()
    cfg0 = BoundaryConfig()
    cfg0.set_level(0)
    cfg2 = BoundaryConfig()
    cfg2.set_level(2)
    assert cfg0.num_nouns != cfg2.num_nouns or cfg0.quote_index != cfg2.quote_index


def test_wrong_answers_zero():
    random.seed(1)
    task = InstructionDataBoundary()
    ex = task.generate_example()
    assert task.score_answer("not the answer", ex) == 0.0
    assert task.score_answer("", ex) == 0.0


def test_answer_is_quoted_substring():
    random.seed(7)
    task = InstructionDataBoundary()
    for _ in range(20):
        ex = task.generate_example()
        assert ex.answer in ex.metadata["quoted"]


def test_both_quote_marks_used_and_levels_run():
    random.seed(42)
    task = InstructionDataBoundary()
    seen = set()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            seen.add(ex.metadata["quoted"][0])
    assert seen == {"\"", "'"}
