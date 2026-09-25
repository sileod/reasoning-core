from reasoning_core.tasks.generated.ua_formal_semantics_r4.lexical_event_coercion import (
    lexical_event_coercion as mod,
)

OPERATORS = mod.OPERATORS
ENTITIES = mod.ENTITIES


def _task():
    return mod.LexicalEventCoercion()


def test_metadata_json_serializable():
    t = _task()
    x = t.generate_example()
    assert isinstance(x.metadata["entity"], str)
    assert isinstance(x.metadata["relations"], list)


def test_score_gold():
    t = _task()
    x = t.generate_example()
    assert t.score_answer(x.answer, x) == 1.0


def test_score_junk():
    t = _task()
    x = t.generate_example()
    assert t.score_answer("", x) == 0.0
    assert t.score_answer("garbage", x) == 0.0
    assert t.score_answer("[x]", x) == 0.0


def test_answer_format():
    t = _task()
    for _ in range(30):
        x = t.generate_example()
        a = x.answer
        assert a.startswith("[")
        assert a.endswith("]")
        assert '"]' in a


def test_ordering_by_strength():
    for entity in ENTITIES:
        rels = mod.sorted_rels(entity)
        strengths = [-v for _, v in rels]
        assert strengths == sorted(strengths)


def test_nested_depth():
    t = _task()
    t.config.depth = 2
    x = t.generate_example()
    assert x.metadata["inner_operator"] is not None


def test_single_depth():
    t = _task()
    t.config.depth = 1
    x = t.generate_example()
    assert x.metadata["inner_operator"] is None


def test_build_match():
    import json
    t = _task()
    t.config.depth = 2
    x = t.generate_example()
    events = mod.build_events(
        x.metadata["operator"], x.metadata["inner_operator"], x.metadata["entity"]
    )
    assert json.loads(x.answer) == events
