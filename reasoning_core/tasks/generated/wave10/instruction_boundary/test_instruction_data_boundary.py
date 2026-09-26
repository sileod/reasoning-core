import re

from reasoning_core.tasks.generated.wave10.instruction_boundary import (
    instruction_data_boundary as mod,
)


def test_gold_scores_one():
    task = mod.InstructionBoundary()
    for _ in range(20):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_junk_scores_zero():
    task = mod.InstructionBoundary()
    e = task.generate_example()
    for junk in ("", "abc", "None", "3.5", "-"):
        assert task.score_answer(junk, e) == 0.0


def test_wrong_number_scores_zero():
    task = mod.InstructionBoundary()
    e = task.generate_example()
    gold = int(e.answer)
    assert task.score_answer(str(gold + 1), e) == 0.0


def test_difficulty_changes_config():
    cfg = mod.InstructionBoundaryConfig()
    base = cfg.n_quotes
    cfg.set_level(5)
    assert cfg.n_quotes > base


def test_random_int_bounded():
    v = mod.do_op("halve", 7)
    assert v == 3


def test_prompt_mentions_quotes():
    task = mod.InstructionBoundary()
    e = task.generate_example()
    txt = mod.InstructionBoundary.render_prompt(task, e.metadata)
    assert "'" in txt
    assert "quoted" in txt


def test_components_in_json():
    import json
    task = mod.InstructionBoundary()
    e = task.generate_example()
    json.dumps(e.metadata.to_dict() if hasattr(e.metadata, "to_dict") else dict(e.metadata))


def test_the_quoted_commands_are_data_not_steps():
    # v1 answered 8807 here by running every quoted command; the numbers total 823.
    task = mod.InstructionBoundary()
    for _ in range(30):
        e = task.generate_example()
        total = sum(target for _op, target in e.metadata.components)
        assert int(e.answer) == mod.do_op(e.metadata.framed_op, total)
    assert mod.do_op("halve", 129 + 200 + 211 + 159 + 124) == 411
