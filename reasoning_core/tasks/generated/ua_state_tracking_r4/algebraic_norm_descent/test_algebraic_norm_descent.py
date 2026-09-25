from reasoning_core.tasks.generated.ua_state_tracking_r4.algebraic_norm_descent import (
    algebraic_norm_descent as mod,
)


def test_gold_scores_one():
    task = mod.AlgebraicNormDescent()
    for _ in range(8):
        x = task.generate_example()
        assert task.score_answer(x.answer, x) == 1.0


def test_junk_scores_less():
    task = mod.AlgebraicNormDescent()
    x = task.generate_example()
    assert task.score_answer('', x) < 1.0
    assert task.score_answer('not a number', x) < 1.0


def test_levels_change_difficulty():
    task = mod.AlgebraicNormDescent()
    task.config.set_level(0)
    s0 = task.config.steps
    task.config.set_level(6)
    s6 = task.config.steps
    assert s6 > s0


def test_norm_is_integer_and_crosschecked():
    task = mod.AlgebraicNormDescent()
    task.config.set_level(6)
    for _ in range(8):
        x = task.generate_example()
        m = x.metadata
        D, q, exps, coeffs, constant = (
            m['D'], m['q'], m['exps'], m['coeffs'], m['constant'])
        gcoeffs = [0] * D
        gcoeffs[0] = constant
        for e, c in zip(exps, coeffs):
            gcoeffs[e] += c
        r = mod._norm_resultant(D, q, gcoeffs)
        mat = mod._norm_matrix(D, q, gcoeffs)
        assert r == mat == int(x.answer)


def test_varied_answers():
    task = mod.AlgebraicNormDescent()
    answers = {int(task.generate_example().answer) for _ in range(24)}
    assert len(answers) > 1
