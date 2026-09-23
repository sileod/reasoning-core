import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

from reasoning_core.tasks.generated.k3_state_tracking_r4.finite_difference_extension.finite_difference_extension import (  # noqa: E501
    FiniteDifferenceExtension,
    finite_diff_extend,
    nth_diff,
    polyval_int,
)


def _build():
    task = FiniteDifferenceExtension()
    task.config.set_level(0)
    return task


def test_gold_scores_one_every_level():
    task = FiniteDifferenceExtension()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(20):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_do_not_score_one():
    task = _build()
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer('', ex) == 0.0
        assert task.score_answer('garbage words here', ex) == 0.0
        assert task.score_answer('1 2 3', ex) == 0.0
        assert task.score_answer('999', ex) == 0.0


def test_extrapolation_matches_polynomial():
    import random
    random.seed(7)
    for _ in range(50):
        d = random.randint(1, 5)
        mag = random.randint(1, 5)
        coeffs = [random.randint(-mag, mag) for _ in range(d + 1)]
        if coeffs[-1] == 0:
            coeffs[-1] = 1
        given_count = d + 2
        values = [polyval_int(coeffs, k) for k in range(given_count)]
        assert all(vc == 0 for vc in nth_diff(values, d + 1))
        target = given_count + random.randint(0, 5)
        assert finite_diff_extend(values, d, target) == polyval_int(coeffs, target)


def test_given_table_has_zero_dplus_difference():
    task = _build()
    for _ in range(20):
        ex = task.generate_example()
        d = ex.metadata.degree
        vals = ex.metadata.given_values
        assert all(v == 0 for v in nth_diff(vals, d + 1))


def test_answer_diversity():
    task = _build()
    answers = set()
    for _ in range(40):
        ex = task.generate_example()
        answers.add(ex.answer)
    assert len(answers) > 10


def test_metadata_json_serializable():
    import json
    task = _build()
    ex = task.generate_example()
    json.dumps(dict(ex.metadata))


def test_answer_count_and_order_enforced():
    task = _build()
    for _ in range(30):
        ex = task.generate_example()
        nq = len(ex.metadata.query_indices)
        assert len(ex.answer.split()) == nq
        wrong_order = ' '.join(reversed(ex.answer.split()))
        assert task.score_answer(wrong_order, ex) == 0.0
        assert task.score_answer(' '.join(['0'] * nq), ex) == 0.0
        assert task.score_answer('1 2 3 4 5', ex) == 0.0


def test_query_indices_increasing_and_beyond_given():
    task = _build()
    for _ in range(20):
        ex = task.generate_example()
        queries = ex.metadata.query_indices
        given_last = ex.metadata.given_indices[-1]
        assert queries == sorted(set(queries))
        assert all(q > given_last for q in queries)
