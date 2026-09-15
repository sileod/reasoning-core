import random
from fractions import Fraction
from itertools import product

from reasoning_core.tasks.generated.k3_invariants_r1.burnside_orbit_count.burnside_orbit_count import (
    BurnsideOrbitCount,
    BurnsideOrbitCountConfig,
    _necklace_group,
    _bracelet_group,
    _grid_group,
    _perm_cycles,
)

TASK = BurnsideOrbitCount


def test_generate_and_score_gold():
    random.seed(2024)
    task = TASK()
    for _ in range(200):
        task.config = BurnsideOrbitCountConfig()
        ex = task.generate_entry()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert len(ex.metadata["perms_cycle_notation"]) == ex.metadata["group_size"]


def test_gold_is_integer_orbit_count():
    random.seed(99)
    task = TASK()
    for level in range(7):
        cfg = BurnsideOrbitCountConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(40):
            ex = task.generate_entry()
            elem = ex.metadata["elementary"]
            gold = Fraction(sum(elem), ex.metadata["group_size"])
            assert Fraction(ex.answer) == gold
            assert Fraction(gold.numerator, gold.denominator) == gold
            assert gold.numerator >= 0


def test_cycles_count_matches_bruteforce_necklace():
    for n in range(2, 7):
        for colors in range(2, 4):
            perms = _necklace_group(n)
            orbits = set()
            for coloring in product(range(colors), repeat=n):
                reps = set()
                for k in range(n):
                    reps.add(tuple(coloring[(i + k) % n] for i in range(n)))
                orbits.add(min(reps))
            gold = Fraction(
                sum(colors ** len(_perm_cycles(p)) for p in perms), len(perms))
            assert len(orbits) == gold.numerator // gold.denominator


def test_group_sizes():
    for n in range(2, 8):
        assert len(_necklace_group(n)) == n
        assert len(_bracelet_group(n)) == 2 * n
    for m in range(2, 5):
        for n in range(2, 5):
            for p in _grid_group(m, n):
                assert len(p) == m * n


def test_score_rejects_junk():
    task = TASK()
    random.seed(5)
    task.config = BurnsideOrbitCountConfig()
    ex = task.generate_entry()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("banana", ex) == 0.0
    gold = Fraction(ex.answer)
    wrong = Fraction(sum(ex.metadata["elementary"]), ex.metadata["group_size"]) + Fraction(7, 3)
    assert task.score_answer(str(wrong), ex) == 0.0
    assert task.score_answer(ex.answer, ex) == 1.0


def test_distinct_answers_occur():
    random.seed(42)
    answers = set()
    task = TASK()
    for _ in range(300):
        task.config = BurnsideOrbitCountConfig()
        ex = task.generate_entry()
        answers.add(ex.answer)
    assert len(answers) >= 3
