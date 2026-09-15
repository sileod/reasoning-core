import random
from fractions import Fraction

from reasoning_core.template import Entry

from .birkhoff import BirkhoffDecomposition, _decompose_birkhoff, _composition


def test_generate_and_score():
    task = BirkhoffDecomposition()
    for level in (0, 3, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert isinstance(ex, Entry)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_scoring_rejects_wrong():
    task = BirkhoffDecomposition()
    task.config.set_level(0)
    ex = task.generate_example()
    assert task.score_answer("garbage", ex) < 1.0
    assert task.score_answer("", ex) < 1.0


def test_difficulty_changes_config():
    task = BirkhoffDecomposition()
    c0 = task.config.to_dict()
    task.config.set_level(task.config.level + 1)
    assert task.config.to_dict() != c0


def test_gold_decomposition_reconstructs_matrix():
    task = BirkhoffDecomposition()
    for level in (0, 2, 5):
        task.config.set_level(level)
        ex = task.generate_example()
        n = ex.metadata["n"]
        matrix = [
            [Fraction(ex.metadata["matrix"][i][j]) for j in range(n)]
            for i in range(n)
        ]
        recon = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for k, p in enumerate(ex.metadata["perms"]):
            perm = [int(x) for x in p.split("-")]
            coeff = Fraction(ex.metadata["coeffs"][k])
            for i in range(n):
                recon[i][perm[i]] += coeff
        assert recon == matrix, "per-answer decomposition must sum back to the prompt matrix"


def test_reproducible_no_seed_reseed():
    task = BirkhoffDecomposition()
    task.generate_example()
    r1 = random.random()
    task.generate_example()
    r2 = random.random()
    assert r1 != r2


def test_permutation_choice_is_valid():
    task = BirkhoffDecomposition()
    task.config.set_level(0)
    ex = task.generate_example()
    n = ex.metadata["n"]
    for p in ex.metadata["perms"]:
        perm = [int(x) for x in p.split("-")]
        assert sorted(perm) == list(range(n))
