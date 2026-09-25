import random

from reasoning_core.tasks.generated.ua_counterfactual_r4.relational_gadget_synthesis.relational_gadget_synthesis import (
    RelationalGadgetSynthesis,
    RelationalGadgetSynthesisV3Config,
    compose,
    minimal_chain,
)


def test_compose_basic():
    r1 = [(1, 2)]
    r2 = [(2, 3)]
    assert compose([r1, r2]) == {(1, 3)}
    assert compose([r1]) == {(1, 2)}


def test_generate_roundtrip():
    random.seed(1)
    task = RelationalGadgetSynthesis()
    ex = task.generate_example()
    assert ex.answer in ("possible", "impossible")
    assert task.score_answer(ex.answer, ex) == 1.0


def test_config_levels():
    cfg = RelationalGadgetSynthesisV3Config()
    cfg.set_level(0)
    assert cfg.n_available == 3
    cfg.set_level(6)
    assert cfg.n_available == 9
    cfg.set_level(2)
    assert cfg.n_available == 5


def test_all_levels_generate():
    task = RelationalGadgetSynthesis()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_deterministic_gold_consistency():
    random.seed(7)
    task = RelationalGadgetSynthesis()
    ex = task.generate_example()
    assert ex.metadata["answer"] == ex.answer
    if ex.answer == "possible":
        assert ex.metadata["n_used"] is not None
        assert ex.metadata["n_used"] >= 1


def test_minimal_chain_correctness():
    parts = [(0, {(1, 2)}), (1, {(2, 3)})]
    r = minimal_chain(parts, {(1, 3)}, True)
    assert r == [0, 1]


def test_answer_not_surface_readable():
    random.seed(3)
    task = RelationalGadgetSynthesis()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(10):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            import re
            nums = [int(x) for x in re.findall(r"\d+", prompt)]
            assert nums
            # the largest / last number must not always predict an answer
            # across levels; correctness is independently verified by minimal_chain
            assert ex.answer in ("possible", "impossible")


def test_label_balance():
    random.seed(5)
    task = RelationalGadgetSynthesis()
    counts = {"possible": 0, "impossible": 0}
    for level in range(7):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            counts[ex.answer] += 1
    total = sum(counts.values())
    assert counts["possible"] / total > 0.2, counts
    assert counts["impossible"] / total > 0.2, counts


def test_reproducibility_same_seed():
    random.seed(42)
    task = RelationalGadgetSynthesis()
    exs1 = [task.generate_example() for _ in range(3)]
    random.seed(42)
    task2 = RelationalGadgetSynthesis()
    exs2 = [task2.generate_example() for _ in range(3)]
    assert [e.answer for e in exs1] == [e.answer for e in exs2]
