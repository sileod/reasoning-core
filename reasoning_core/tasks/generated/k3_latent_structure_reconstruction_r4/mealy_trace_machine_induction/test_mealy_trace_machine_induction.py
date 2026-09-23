import random

from reasoning_core.template import Task

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.mealy_trace_machine_induction.mealy_trace_machine_induction import (
    MealyTraceMachineInduction,
    _parse_answer,
)


def test_gold_scores_one():
    task = MealyTraceMachineInduction()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_zero():
    task = MealyTraceMachineInduction()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("garbage", ex) == 0.0
    assert task.score_answer("q0 --a--> q9/0", ex) == 0.0


def test_difficulty_changes_config():
    task = MealyTraceMachineInduction()
    base = task.config.n_states
    task.config.set_level(6)
    assert task.config.n_states > base


def test_parse(): 
    d = _parse_answer("q0 --a--> q1/0 ; q0 --b--> q2/1")
    assert d == {("q0", "a"): ("q1", "0"), ("q0", "b"): ("q2", "1")}


def test_metadata_serializable():
    import json
    task = MealyTraceMachineInduction()
    task.config.set_level(5)
    for _ in range(10):
        ex = task.generate_example()
        json.dumps(ex.metadata)


def test_deterministic():
    random.seed(12345)
    task = MealyTraceMachineInduction()
    ex1 = task.generate_example()
    random.seed(12345)
    ex2 = task.generate_example()
    assert ex1.answer == ex2.answer


def test_answer_is_total_function():
    task = MealyTraceMachineInduction()
    for level in (0, 2, 3, 5, 6):
        task.config.set_level(level)
        for _ in range(15):
            ex = task.generate_example()
            mapped = _parse_answer(ex.answer)
            assert mapped is not None
            states = sorted({s for (s, _i) in mapped}, key=lambda s: int(s[1:]))
            names = [f"q{i}" for i in range(len(states))]
            assert states == names, "state names must be canonical q0..qn"
            last = int(states[-1][1:]) if states else -1
            assert len(states) == last + 1, "state names must be contiguous"
            expected_keys = set()
            for s in states:
                for i in ("a", "b"):
                    expected_keys.add((s, i))
            assert set(mapped.keys()) == expected_keys, "every state, both inputs"
            for (s, i), (ns, o) in mapped.items():
                assert ns in states
                assert o in ("0", "1")
            # number of states matches minimized machine size from metadata
            assert len(states) == ex.metadata["m"]


def test_answer_difficulty_monotonic_state_count():
    task = MealyTraceMachineInduction()
    counts = []
    for level in (0, 2, 4, 6):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            counts.append(ex.metadata["m"])
    # highest level should occasionally exceed lowest
    assert max(counts) > min(counts)


def test_no_constant_answer():
    task = MealyTraceMachineInduction()
    answers = set()
    for level in (0, 2, 3, 5):
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            answers.add(ex.answer)
    assert len(answers) > 5, "must not collapse to a constant answer"
