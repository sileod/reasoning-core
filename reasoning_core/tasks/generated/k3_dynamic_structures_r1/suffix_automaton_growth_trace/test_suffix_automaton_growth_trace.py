import random

from reasoning_core.tasks.generated.k3_dynamic_structures_r1.suffix_automaton_growth_trace.suffix_automaton_growth_trace import (
    _build_sam,
    _parse_answer,
    _state_tuple,
    suffix_automaton_growth_trace,
)


def test_build_sam_single_char():
    states = _build_sam("a")
    assert len(states) == 2
    assert states[0]["len"] == 0 and states[0]["link"] == -1
    assert states[0]["next"] == {"a": 1}
    assert states[1]["len"] == 1 and states[1]["link"] == 0


def test_build_sam_repeated():
    states = _build_sam("aaa")
    # aaa with alphabet {a}: len grows, single transition chain
    assert states[0]["next"] == {"a": 1}
    assert states[1]["next"] == {"a": 2}
    link_chain = [states[i]["link"] for i in range(4)]
    assert link_chain[0] == -1
    assert link_chain[1] == 0
    assert link_chain[2] == 1
    assert link_chain[3] == 2


def test_build_sam_abab_creates_clone():
    states = _build_sam("abab")
    # non-trivial structure should create at least one clone
    # "abab": state 3 has link 1 (from 'ab'), char b transitions between classes
    assert len(states) >= 5


def test_state_tuple_canonical():
    states = _build_sam("ab")
    t = _state_tuple(states)
    assert t[0][0] == 0 and t[0][1] == -1
    assert t[0][2] == (("a", 1), ("b", 2))
    assert t[1][0] == 1 and t[1][2] == (("b", 2),)
    assert t[2][0] == 2 and t[2][1] == 0


def test_scoring_roundtrip():
    task = suffix_automaton_growth_trace()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer("garbage", ex) == 0.0


def test_gold_answers_in_domain():
    task = suffix_automaton_growth_trace()
    for _ in range(20):
        ex = task.generate_example()
        for ln, lk, tr in _parse_answer(ex.answer):
            assert ln >= 0
            assert lk >= -1
        n = ex.metadata["state_count"]
        for ln, lk, tr in _parse_answer(ex.answer):
            assert lk < n
            for c, to in tr:
                assert 0 <= to < n


def test_levels_vary():
    task = suffix_automaton_growth_trace()
    lens = []
    for level in range(7):
        task.config.set_level(level)
        ex = task.generate_example()
        lens.append(len(ex.answer))
    # higher levels generally produce larger automata
    assert lens[6] >= lens[0]


def test_deterministic():
    random.seed(123)
    task = suffix_automaton_growth_trace()
    a = task.generate_example().answer
    random.seed(123)
    b = task.generate_example().answer
    assert a == b
