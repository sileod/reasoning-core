import pytest

import reasoning_core.tasks.generated.k3_invariants_r1.cyk_chart_membership.cyk_chart_membership as mod


@pytest.fixture
def task_cls():
    return mod.CykChartMembership


def test_generate_and_score(task_cls):
    t = task_cls()
    for level in (0, 2, 5):
        t.config.set_level(level)
        for _ in range(20):
            x = t.generate_example()
            assert t.score_answer(x.answer, x) == 1.0
            assert t.score_answer("", x) < 1.0
            assert t.score_answer("junk", x) < 1.0


def test_metadata_json_and_dedup(task_cls):
    t = task_cls()
    t.config.set_level(3)
    x = t.generate_example()
    assert x.answer == (str(x.metadata["deriv_count"])
                        if x.metadata["query_type"] == "count"
                        else (" ".join(x.metadata["cell"]) if x.metadata["cell"]
                              else "EMPTY"))


def test_difficulty_changes(task_cls):
    t = task_cls()
    t.config.set_level(0)
    base = t.config.string_len
    t.config.set_level(6)
    assert t.config.string_len > base


def test_summary_present(task_cls):
    assert task_cls.summary


def test_meta_present():
    assert mod.TASK_META["hypothesis"] == "P001"
