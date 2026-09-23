import pytest

from reasoning_core.tasks.generated.k3_surface_invariance_r4.gauss_link_code_walk.gauss_link_code_walk import (
    GaussLinkCodeWalk,
    _decompose,
    _parse_writhes,
)


@pytest.fixture
def task():
    return GaussLinkCodeWalk()


def test_gold_scores_one(task):
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_wrong_answers_score_less(task):
    ex = task.generate_example()
    golds = _parse_writhes(ex.answer)
    n = len(golds)
    wrong = ",".join(str(w + 1) for w in golds)
    if _parse_writhes(wrong) == golds:
        wrong = ",".join(str(w - 1) for w in golds)
    assert task.score_answer(wrong, ex) < 1.0
    assert task.score_answer("", ex) < 1.0
    assert task.score_answer("junk", ex) < 1.0
    assert task.score_answer("not a number", ex) < 1.0


def test_answer_is_valid_writhe_list(task):
    for _ in range(30):
        ex = task.generate_example()
        vals = _parse_writhes(ex.answer)
        assert vals is not None
        assert len(vals) >= 1
        comp = _decompose([[c, s] for c, s in ex.metadata["crossings"]])
        assert comp == vals


def test_all_levels_generate(task):
    for level in range(0, 7):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0
        assert 0 < len(ex.prompt) < 2048


def test_summary_design_meta(task):
    assert task.summary.strip()
    assert "comma-separated" in task.summary
    assert task.design_choice == (
        "Generate diagrams with mixed over/under crossings and require answers as "
        "a single comma-separated list of writhe per component, ordered by first appearance."
    )
