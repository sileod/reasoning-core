import random

from reasoning_core.tasks.generated.k3_language_implementation_r4.archive_symbol_binding_order.archive_symbol_binding_order import (
    ArchiveSymbolBindingOrder,
    _link,
    _format_answer,
)


def test_example_generates():
    task = ArchiveSymbolBindingOrder()
    ex = task.generate_example()
    assert ex.prompt
    assert ex.answer
    assert ex.metadata is not None


def test_gold_scores_one():
    random.seed(1)
    task = ArchiveSymbolBindingOrder()
    for _ in range(20):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_junk_scores_less():
    random.seed(2)
    task = ArchiveSymbolBindingOrder()
    for _ in range(10):
        ex = task.generate_example()
        assert task.score_answer("", ex) < 1.0
        assert task.score_answer("garbage", ex) < 1.0
        assert task.score_answer("reajrjrje9595!", ex) < 1.0


def test_whitespace_insensitive():
    task = ArchiveSymbolBindingOrder()
    ex = task.generate_example()
    assert task.score_answer("  " + ex.answer.replace("\n", "   ") + "\n", ex) == 1.0


def test_levels_difficulty():
    random.seed(3)
    for lvl in range(7):
        task = ArchiveSymbolBindingOrder()
        task.config.set_level(lvl)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0


def test_link_deterministic():
    random.seed(5)
    task = ArchiveSymbolBindingOrder()
    ex = task.generate_example()
    extracted, table = _link(ex.metadata['commands'])
    assert _format_answer(extracted, table) == ex.answer


def test_metadata_json_serializable():
    import json
    random.seed(6)
    task = ArchiveSymbolBindingOrder()
    for _ in range(10):
        ex = task.generate_example()
        json.dumps(dict(ex.metadata))


def test_no_internal_in_bindings():
    random.seed(7)
    task = ArchiveSymbolBindingOrder()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(20):
            ex = task.generate_example()
            bindings = ex.answer.split("\n")[1]
            assert not any("=I" in part for part in bindings.split())


def test_bindings_nonempty_and_sorted():
    random.seed(8)
    task = ArchiveSymbolBindingOrder()
    for lvl in range(7):
        task.config.set_level(lvl)
        for _ in range(20):
            ex = task.generate_example()
            lines = ex.answer.split("\n")
            assert len(lines) == 2
            names = [p.split("=")[0] for p in lines[1].replace("Bindings:", "").split()]
            assert names == sorted(names)
            assert lines[0].startswith("Extracted:")


def test_extracted_in_link_order():
    random.seed(9)
    task = ArchiveSymbolBindingOrder()
    task.config.set_level(4)
    for _ in range(40):
        ex = task.generate_example()
        extracted, _table = _link(ex.metadata['commands'])
        ans_extracted = ex.answer.split("\n")[0].replace("Extracted:", "").split()
        assert ans_extracted == (['none'] if not extracted else extracted)

