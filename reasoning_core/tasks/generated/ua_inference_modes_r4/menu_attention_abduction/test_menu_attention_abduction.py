from reasoning_core.tasks.generated.ua_inference_modes_r4.menu_attention_abduction.menu_attention_abduction import (
    MenuAttentionAbduction,
    _select,
)


def _task():
    return MenuAttentionAbduction()


def test_modes_balanced_and_score_one():
    t = _task()
    labels = {"yes": 0, "no": 0}
    item_labels = {}
    kinds = {}
    for _ in range(200):
        ex = t.generate_example()
        assert t.score_answer(ex.answer, ex) == 1.0
        assert ex.answer == ex.metadata["answer"]
        kinds[ex.metadata["kind"]] = kinds.get(ex.metadata["kind"], 0) + 1
        if ex.metadata["kind"] == "attention":
            labels[ex.answer] = labels.get(ex.answer, 0) + 1
        else:
            item_labels[ex.answer] = item_labels.get(ex.answer, 0) + 1
    assert set(kinds) == {"preference", "attention"}
    total = sum(labels.values())
    assert total > 0 and max(labels.values()) / total < 0.7


def test_preference_gold_matches_rule():
    t = _task()
    for _ in range(200):
        ex = t.generate_example()
        if ex.metadata["kind"] != "preference":
            continue
        m = ex.metadata
        rank = {it: i for i, it in enumerate(m["pref"])}
        gold = _select(m["menu"][0], m["menu"][1], m["attention"], rank)
        assert gold == ex.answer
        assert ex.answer in m["menu"]


def test_metadata_is_json_serializable():
    import json
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(10):
            ex = t.generate_example()
            json.dumps(ex.to_dict())


def test_attention_gold_matches_membership():
    t = _task()
    for _ in range(200):
        ex = t.generate_example()
        if ex.metadata["kind"] != "attention":
            continue
        m = ex.metadata
        assert (ex.answer == "yes") == (m["query"] in m["attention"])


def test_levels_generate_all():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(20):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0


def test_preference_limited_consideration_inverts_choice():
    # Preference says first > second, but only second considered -> selects second.
    rank = {"A": 0, "B": 1}
    assert _select("A", "B", ["B"], rank) == "B"
    # Neither considered -> default is first-listed.
    assert _select("A", "B", [], rank) == "A"


def test_score_junk():
    t = _task()
    ex = t.generate_example()
    assert t.score_answer("", ex) == 0.0
    assert t.score_answer("garbage", ex) == 0.0
    assert t.score_answer("import fakemodule", ex) == 0.0


def test_constant_guess_balanced_binary():
    t = _task()
    for level in range(7):
        t.config.set_level(level)
        counts = {}
        for _ in range(120):
            ex = t.generate_example()
            counts[ex.answer] = counts.get(ex.answer, 0) + 1
        n = sum(counts.values())
        max_frac = max(counts.values()) / n if n else 0
        assert max_frac <= 0.7, (level, counts)
