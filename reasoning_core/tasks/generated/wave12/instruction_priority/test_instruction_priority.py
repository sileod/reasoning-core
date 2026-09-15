import random

from reasoning_core.tasks.generated.wave12.instruction_priority.instruction_priority import (
    InstructionPriority,
    _check_final,
    _contradicts,
)


def test_roundtrip_and_score():
    random.seed(1002768851)
    task = InstructionPriority()
    for _ in range(200):
        entry = task.generate_example()
        assert task.score_answer(entry.answer, entry) == 1.0
        assert entry.answer in ("yes", "no")
        prompt = task.render_prompt(entry.metadata)
        assert prompt.count("exactly yes or no") == 1


def test_balance():
    random.seed(7)
    task = InstructionPriority()
    counts = {"yes": 0, "no": 0}
    for _ in range(2000):
        entry = task.generate_example()
        counts[entry.answer] += 1
    frac = max(counts.values()) / sum(counts.values())
    assert frac < 0.7, counts


def test_difficulty_changes():
    cfg = InstructionPriority.config_cls()
    cfg.set_level(0)
    a = (cfg.n_instructions, cfg.max_rank)
    cfg.set_level(5)
    b = (cfg.n_instructions, cfg.max_rank)
    assert a != b


def test_contradicts():
    assert _contradicts("open the doors", "open the doors")
    assert _contradicts("open the doors", "do not open the doors")
    assert not _contradicts("open the doors", "raise the flag")


def test_check_final_domains():
    assert _check_final([("do", 3, "open the doors")], "open the doors") == "yes"
    assert _check_final([("do_not", 3, "do not open the doors")], "open the doors") == "no"
    assert _check_final([("do", 3, "raise the flag")], "open the doors") is None
    assert _check_final([("do", 3, "open the doors"), ("do_not", 3, "do not open the doors")],
                        "open the doors") is None


def test_no_repeat_prompt_same_answer():
    random.seed(3)
    task = InstructionPriority()
    seen = {}
    for _ in range(2000):
        entry = task.generate_example()
        prompt = task.render_prompt(entry.metadata)
        if prompt in seen:
            assert seen[prompt] == entry.answer
        else:
            seen[prompt] = entry.answer
