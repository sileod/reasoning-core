import random

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.repetition_restitution_witnesses.repetition_restitution_witnesses import (
    RepetitionRestitutionWitnesses,
)


def _task(level=0):
    t = RepetitionRestitutionWitnesses()
    t.config.set_level(level)
    return t


def test_generate_and_score_all_levels():
    for level in range(7):
        t = _task(level)
        for _ in range(20):
            ex = t.generate_example()
            assert t.score_answer(ex.answer, ex) == 1.0
            assert ex.prompt


def test_invalid_answers_rejected():
    t = _task(2)
    ex = t.generate_example()
    assert t.score_answer("", ex) < 1.0
    assert t.score_answer("junk input here", ex) < 1.0
    assert t.score_answer("import fakemodule", ex) < 1.0
    assert t.score_answer(None, ex) < 1.0


def test_answer_matches_metadata():
    for level in (0, 3, 6):
        t = _task(level)
        ex = t.generate_example()
        readings = ex.metadata["readings"]
        tokens = [
            "None" if r["witness"] is None else f"E{r['witness']}"
            for r in readings
        ]
        assert ex.answer == " ".join(tokens)


def test_no_constant_answer():
    answers = set()
    t = _task(6)
    for _ in range(60):
        answers.add(t.generate_example().answer)
    assert len(answers) > 5


def test_readings_varied():
    for level in (0, 3, 6):
        t = _task(level)
        tokens_seen = set()
        for _ in range(60):
            ex = t.generate_example()
            tokens_seen.update(set(ex.answer.split()))
        assert "None" in tokens_seen
        assert any(tok.startswith("E") for tok in tokens_seen)


def test_metadata_json_serializable():
    import json

    t = _task(3)
    ex = t.generate_example()
    json.dumps(dict(ex.metadata))


def test_repetitive_needs_same_subject():
    from reasoning_core.tasks.generated.ua_scope_and_binding_r4.repetition_restitution_witnesses.repetition_restitution_witnesses import (
        _find_repetitive_witness,
    )

    events = [
        {"subject": "Ada", "action": "open", "object": "door", "state": "open"},
        {"subject": "Ben", "action": "open", "object": "door", "state": "open"},
        {"subject": "Ada", "action": "open", "object": "box", "state": "open"},
    ]
    assert _find_repetitive_witness(events, 2) == 0
    assert _find_repetitive_witness(events, 1) is None


def test_restitutive_interrupted_by_intermediate_change():
    from reasoning_core.tasks.generated.ua_scope_and_binding_r4.repetition_restitution_witnesses.repetition_restitution_witnesses import (
        _find_restitutive_witness,
    )

    events = [
        {"subject": "Ada", "action": "open", "object": "door", "state": "open"},
        {"subject": "Ben", "action": "close", "object": "door", "state": "closed"},
        {"subject": "Cara", "action": "open", "object": "door", "state": "open"},
    ]
    # focus E2 (open): most recent prior touch E1 left the door closed -> interrupted -> None
    assert _find_restitutive_witness(events, 2) is None
    # focus E1 (closed): most recent prior touch E0 left the door open -> interrupted -> None
    assert _find_restitutive_witness(events, 1) is None
    untouched = [
        {"subject": "Ada", "action": "open", "object": "door", "state": "open"},
        {"subject": "Ben", "action": "open", "object": "box", "state": "open"},
    ]
    assert _find_restitutive_witness(untouched, 1) is None
