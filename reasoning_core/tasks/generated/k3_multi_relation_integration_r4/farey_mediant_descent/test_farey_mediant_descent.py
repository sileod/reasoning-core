from reasoning_core.tasks.generated.k3_multi_relation_integration_r4.farey_mediant_descent.farey_mediant_descent import (
    FareyMediantDescent,
    FareyMediantDescentV1Config,
    _path_to_fraction,
    _reconstruct,
    gcd,
)


def test_level_zero_diversity():
    task = FareyMediantDescent()
    answers = set()
    for _ in range(60):
        x = task.generate_example()
        answers.add(x.answer)
    assert len(answers) >= 4


def test_gold_reconstructs_fraction():
    task = FareyMediantDescent()
    for level in (0, 2, 5, 6):
        cfg = FareyMediantDescentV1Config().set_level(level)
        task.config = cfg
        for _ in range(80):
            x = task.generate_example()
            n, d = x.metadata["num"], x.metadata["den"]
            assert _reconstruct(x.answer) == (n, d)
            assert gcd(n, d) == 1
            assert 0 < n < d
            assert _path_to_fraction(n, d) == x.answer


def test_difficulty_increases():
    l0 = FareyMediantDescentV1Config().set_level(0)
    l6 = FareyMediantDescentV1Config().set_level(6)
    assert l0.denom_max < l6.denom_max


def test_score_answer():
    task = FareyMediantDescent()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0
    assert task.score_answer("L" if x.answer != "L" else "R", x) == 0.0
    assert task.score_answer("", x) == 0.0
