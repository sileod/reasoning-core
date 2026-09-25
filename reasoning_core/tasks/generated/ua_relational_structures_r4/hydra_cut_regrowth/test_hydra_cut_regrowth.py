import random

from reasoning_core.tasks.generated.ua_relational_structures_r4.hydra_cut_regrowth.hydra_cut_regrowth import (
    HydraCutRegrowth,
    _available_depths,
    _count_heads,
    _cut,
    _render,
)


def _gold_heads(initial_str, depth_seq):
    root = _parse(initial_str)
    for d in depth_seq:
        assert _cut(root, d), "cut failed on parsed tree"
    return _count_heads(root, True)


def _parse(s):
    i = 0
    n = len(s)

    def parse_node():
        nonlocal i
        if s[i] == "h":
            i += 1
            return []
        assert s[i] == "(", s[i]
        i += 1
        children = []
        while s[i] != ")":
            if s[i] == " ":
                i += 1
                continue
            children.append(parse_node())
        i += 1
        return children

    return parse_node()


def test_example_round_trip():
    random.seed(1)
    task = HydraCutRegrowth()
    for _ in range(40):
        x = task.generate_example()
        assert x.answer.isdigit()
        assert int(x.answer) >= 1
        assert task.score_answer(x.answer, x) == 1.0
        assert task.score_answer("", x) == 0.0
        assert task.score_answer("junk", x) == 0.0
        assert int(x.answer) == _gold_heads(x.metadata["initial_str"], x.metadata["depth_seq"])


def test_difficulty_changes():
    task = HydraCutRegrowth()
    l0 = task.config.set_level(0)
    l6 = task.config.set_level(6)
    assert l6.num_cuts >= l0.num_cuts
    assert l6.max_depth >= l0.max_depth


def test_all_levels_generate():
    for level in range(7):
        random.seed(99)
        task = HydraCutRegrowth()
        x = task.generate_example()
        assert int(x.answer) >= 1


def test_independent_verifier_every_level():
    for level in range(7):
        random.seed(100 + level)
        task = HydraCutRegrowth()
        task.config.set_level(level)
        for _ in range(30):
            x = task.generate_example()
            assert int(x.answer) == _gold_heads(
                x.metadata["initial_str"], x.metadata["depth_seq"]
            )


def test_prompt_stable_prose():
    random.seed(7)
    task = HydraCutRegrowth()
    x = task.generate_example()
    p = x.metadata["_prompt_tokens"]
    assert isinstance(p, int)
    assert _render(_parse(x.metadata["initial_str"])) == x.metadata["initial_str"]
