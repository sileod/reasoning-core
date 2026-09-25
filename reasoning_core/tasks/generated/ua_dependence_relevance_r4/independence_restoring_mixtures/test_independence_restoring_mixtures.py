import random
from fractions import Fraction

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.independence_restoring_mixtures.independence_restoring_mixtures import (
    IndependenceRestoringMixtures,
    _moments,
    _cov_poly,
    interior_roots,
)


def _check_independent(g0, g1, w):
    a0, b0, c0 = _moments(g0)
    a1, b1, c1 = _moments(g1)
    ex = w * a0 + (1 - w) * a1
    ey = w * b0 + (1 - w) * b1
    exy = w * c0 + (1 - w) * c1
    return exy == ex * ey


def _parse_grid(fmt_line):
    # fmt_line like "X=0,Y=0: 1/4; X=0,Y=1: 1/4; X=1,Y=0: 1/4; X=1,Y=1: 1/4"
    g = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    for part in fmt_line.split(";"):
        seg = part.strip()
        if not seg:
            continue
        coord, val = seg.split(":")
        x = int(coord.split(",")[0].split("=")[1])
        y = int(coord.split(",")[1].split("=")[1])
        g[x][y] = Fraction(val.strip())
    return g


def test_gold_scores_and_independence():
    for level in range(7):
        for trial in range(5):
            random.seed(1000 * level + trial)
            task = IndependenceRestoringMixtures()
            task.config.set_level(level)
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer("", ex) < 1.0
            assert task.score_answer("junk", ex) < 1.0
            w = Fraction(ex.metadata["answer"])
            for pair in ex.metadata["strata"]:
                g0 = _parse_grid(pair[0][0])
                g1 = _parse_grid(pair[1][0])
                assert _check_independent(g0, g1, w)


def test_only_one_interior_root_is_answer():
    for level in range(7):
        for trial in range(5):
            random.seed(7777 * level + trial)
            task = IndependenceRestoringMixtures()
            task.config.set_level(level)
            ex = task.generate_example()
            w = Fraction(ex.metadata["answer"])
            for pair in ex.metadata["strata"]:
                g0 = _parse_grid(pair[0][0])
                g1 = _parse_grid(pair[1][0])
                A, B, C = _cov_poly(g0, g1)
                assert interior_roots(A, B, C) == [w]


def test_difficulty_changes_config():
    task = IndependenceRestoringMixtures()
    task.config.set_level(0)
    s0 = task.config.strata
    task.config.set_level(6)
    s6 = task.config.strata
    assert s6 >= s0
