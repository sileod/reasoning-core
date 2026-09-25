import random

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.simplicial_operator_normalization.simplicial_operator_normalization import (
    SimplicialOperatorNormalization,
    _simulate,
    normalize,
    _format_answer,
)


def test_normalize_canonical_structure():
    s_block, d_block = normalize([('d', 0), ('s', 0)])
    assert (s_block, d_block) == ([], [])
    s_block, d_block = normalize([('d', 1), ('s', 0)])
    assert (s_block, d_block) == ([], [])
    s_block, d_block = normalize([('s', 1), ('s', 1), ('d', 0)])
    assert (s_block, d_block) == ([1, 1], [0])


def test_simulation_consistency():
    rng = random.Random(1234)
    for _ in range(2000):
        n = rng.randint(1, 6)
        word = [(rng.choice(('d', 's')), rng.randint(0, 5)) for _ in range(n)]
        start = list(range(7))
        try:
            orig = _simulate(list(start), word)
        except IndexError:
            continue
        s_block, d_block = normalize(list(word))
        canon = [('s', x) for x in s_block] + [('d', x) for x in d_block]
        assert _simulate(list(start), canon) == orig


def test_full_roundtrip_all_levels():
    for level in range(7):
        task = SimplicialOperatorNormalization()
        task.config.set_level(level)
        for _ in range(30):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            assert task.score_answer("", ex) == 0.0
            assert task.score_answer("garbage", ex) == 0.0


def test_format_answer():
    assert _format_answer([1, 3], [0, 2]) == "omitted=[1, 3]; repeated=[0, 2]"
    assert _format_answer([], []) == "omitted=[]; repeated=[]"
