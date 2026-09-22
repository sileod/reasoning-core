from reasoning_core.tasks.generated.k3_formal_semantics_r4.ccg_category_combination import (
    ccg_category_combination as mod,
)


def _task():
    return mod.CcgCategoryCombination()


def test_metadata_json_serializable():
    t = _task()
    x = t.generate_example()
    assert isinstance(x.metadata["words"], list)


def test_score_gold():
    t = _task()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1.0


def test_score_junk():
    t = _task()
    t.config.seq_len = 3
    x = t.generate_example()
    assert t.score_answer("", x) == 0.0
    assert t.score_answer("garbage", x) == 0.0
    assert t.score_answer("(S\\NP)", x) == 0.0


def test_reduce_consistency():
    for _ in range(50):
        target, words, seq = mod.generate_entry_for(3)
        assert mod.reduce_all(seq) == target
        assert target in mod.ATOMS


def test_combination_rules():
    assert mod.combine("(NP/N)", "N") == "NP"
    assert mod.combine("NP", "(S\\NP)") == "S"
    assert mod.combine("(NP/N)", "(N/N)") == "(NP/N)"
