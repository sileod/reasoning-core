import random
import sys
from pathlib import Path

import sympy

sys.path.insert(0, str(Path(__file__).parent))

from cluster_seed_evolution import ClusterSeedEvolution


def test_generate_and_score_gold():
    random.seed(123)
    task = ClusterSeedEvolution()
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(10):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_zero():
    random.seed(7)
    task = ClusterSeedEvolution()
    for level in (0, 5):
        task.config.set_level(level)
        x = task.generate_example()
        assert task.score_answer("", x) < 1.0
        assert task.score_answer("not an expression", x) < 1.0
        assert task.score_answer(42, x) < 1.0


def test_equivalent_expression_scores_one():
    random.seed(99)
    task = ClusterSeedEvolution()
    task.config.set_level(2)
    x = task.generate_example()
    md = x.metadata
    symbols = [sympy.Symbol(n) for n in md["symbols"]]
    g = sympy.sympify(md["answer"], locals={str(s): s for s in symbols})
    g2 = sympy.together(sympy.cancel(g * 2 - g))  # 2g - g = g
    assert task.score_answer(sympy.sstr(sympy.cancel(g * 2 - g)), x) == 1.0


def test_level_changes_config():
    task = ClusterSeedEvolution()
    task.config.set_level(0)
    base = task.config.rank
    task.config.set_level(6)
    assert task.config.rank >= base


def test_mutation_check_passes():
    random.seed(5)
    task = ClusterSeedEvolution()
    task.config.set_level(6)
    for _ in range(20):
        x = task.generate_example()
        assert x.answer  # non-empty gold
        assert task.score_answer(x.answer, x) == 1.0
