import random

import reasoning_core.tasks.generated.k3_formal_logic_r4.unknown_join_survivors.unknown_join_survivors as mod


def test_gold_scores_one():
    task = mod.UnknownJoinSurvivors()
    for _ in range(40):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_answer_deterministic_under_seed():
    task = mod.UnknownJoinSurvivors()
    task.config.set_level(3)
    random.seed(1234)
    e1 = task.generate_entry()
    random.seed(1234)
    e2 = task.generate_entry()
    assert e1.answer == e2.answer
    assert e1.metadata["survivors"] == e2.metadata["survivors"]


def test_junk_scores_zero():
    task = mod.UnknownJoinSurvivors()
    e = task.generate_example()
    for bad in ("", " ", "reajrjrje9595!", "r0,s0", "[r0,s0]"):
        assert task.score_answer(bad, e) == 0.0


def test_atom_kinds_and_3vl():
    row = {"p": 2, "x": None, "y": 0}
    assert mod._atom_eval(row, ("cmp", "x", "=", None)) is None
    assert mod._atom_eval(row, ("cmp", "x", "=", 1)) is None
    assert mod._atom_eval(row, ("cmp", "y", "=", 0)) is True
    assert mod._atom_eval(row, ("cmp", "y", "<", 0)) is False
    assert mod._formula_eval(row, [("cmp", "x", "=", 1)], True) is None
    assert mod._formula_eval(row, [("cmp", "y", "<", 0)], True) is True


def test_bag_join_duplicates_and_ordering():
    R = [{"pk": "r0", "p": 2, "x": 1},
         {"pk": "r1", "p": 2, "x": 2},
         {"pk": "r2", "p": None, "x": 0}]
    S = [{"pk": "s0", "p": 2, "y": 0},
         {"pk": "s1", "p": 1, "y": 1}]
    joined = mod._bag_join(R, S)
    assert [ (j["rpk"], j["spk"]) for j in joined ] == \
           [("r0", "s0"), ("r1", "s0")]
    assert mod._answer_of(joined) == "(r0,s0) (r1,s0)"


def test_answer_of_empty():
    assert mod._answer_of([]) == "[]"


def test_survivor_answer_matches_metadata():
    task = mod.UnknownJoinSurvivors()
    for _ in range(30):
        e = task.generate_entry()
        meta_pairs = [tuple(p) for p in e.metadata["survivors"]]
        parsed = [] if e.answer == "[]" else [
            tuple(tok.strip("()").split(",")) for tok in e.answer.split()
        ]
        assert meta_pairs == parsed


def test_difficulty_changes_config():
    task = mod.UnknownJoinSurvivors()
    c0 = task.config.__dict__.copy()
    task.config.set_level(task.config.level + 1)
    assert task.config.__dict__ != c0
    task.config.set_level(0)


def test_metadata_json_roundtrip():
    import json
    task = mod.UnknownJoinSurvivors()
    e = task.generate_entry()
    json.dumps(dict(e.metadata))
