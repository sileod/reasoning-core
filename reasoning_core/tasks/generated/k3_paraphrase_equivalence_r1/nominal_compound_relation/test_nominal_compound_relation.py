import random

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r1.nominal_compound_relation.nominal_compound_relation import (
    NominalCompoundRelation,
    _parse_indices,
)


def _build(task, level):
    task.config.set_level(level)
    return task.generate_example()


def test_roundtrip_all_levels():
    t = NominalCompoundRelation()
    for level in [0, 1, 2, 3, 4, 5, 6]:
        x = _build(t, level)
        assert t.score_answer(x.answer, x) == 1.0
        assert _parse_indices(x.answer) == x.metadata["matched"]


def test_gold_matches_generated_relations():
    for _ in range(50):
        t = NominalCompoundRelation()
        t.config.set_level(random.randint(0, 6))
        x = t.generate_example()
        rels = set(x.metadata["compound_preps"])
        for j, prep in enumerate(x.metadata["paraphrase_preps"]):
            should_match = prep in rels
            assert (j in x.metadata["matched"]) == should_match


def test_unmatched_garbage():
    t = NominalCompoundRelation()
    t.config.set_level(3)
    x = t.generate_example()
    assert t.score_answer("", x) == 0.0
    assert t.score_answer("garbage", x) == 0.0
    assert t.score_answer("[1", x) == 0.0


def test_label_balance():
    t = NominalCompoundRelation()
    counts = {}
    for _ in range(200):
        t.config.set_level(3)
        x = t.generate_example()
        counts[len(x.metadata["matched"])] = counts.get(len(x.metadata["matched"]), 0) + 1
    assert len(counts) >= 2


def test_parse_indices():
    assert _parse_indices("[1, 3]") == [1, 3]
    assert _parse_indices("[]") == []
    assert _parse_indices("[0]") == [0]
