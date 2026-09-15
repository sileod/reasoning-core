"""Tests for the Allen interval composition task."""

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import allen_interval_composition as m


def test_table_complete():
    for ra in m.RELATIONS:
        for rb in m.RELATIONS:
            cell = m.TABLE[(ra, rb)]
            assert cell
            for rc in cell:
                assert rc in m.RELATIONS


def test_known_cells():
    assert m.TABLE[("e", "e")] == frozenset({"e"})
    assert m.TABLE[("b", "d")] == frozenset({"b"})
    assert m.TABLE[("m", "bi")] == frozenset({"bi", "d", "mi", "oi", "si"})


def test_basic_compose():
    random.seed(1)
    chain = [frozenset({"e"}), frozenset({"b"})]
    assert m.compose_chain(chain) == sorted(m.TABLE[("e", "b")])


def test_associativity_chunking():
    random.seed(7)
    for _ in range(200):
        a = frozenset(random.sample(m.RELATIONS, random.randint(1, 3)))
        b = frozenset(random.sample(m.RELATIONS, random.randint(1, 3)))
        c = frozenset(random.sample(m.RELATIONS, random.randint(1, 3)))
        left = m.compose_chain([m._compose_step(a, b), c])
        right = m.compose_chain([a, m._compose_step(b, c)])
        assert set(left) == set(right)


def test_score_gold_and_junk():
    random.seed(3)
    config = m.AllenIntervalCompositionV1Config()
    config.set_level(0)
    task = m.AllenIntervalComposition(config=config)
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("zzz", ex) == 0.0
    assert task.score_answer("b,b", ex) == 0.0


def test_answer_format_and_domain():
    random.seed(11)
    config = m.AllenIntervalCompositionV1Config()
    config.set_level(6)
    task = m.AllenIntervalComposition(config=config)
    for _ in range(50):
        ex = task.generate_example()
        ans = ex.answer
        syms = ans.split(",")
        assert syms == sorted(syms, key=lambda s: m.ORDER[s])
        assert len(set(syms)) == len(syms)
        assert all(s in m.RELATIONS for s in syms)


def test_level_scaling():
    c0 = m.AllenIntervalCompositionV1Config()
    c0.set_level(0)
    c6 = m.AllenIntervalCompositionV1Config()
    c6.set_level(6)
    assert c6.n_steps > c0.n_steps
    assert c6.max_disj >= c0.max_disj
