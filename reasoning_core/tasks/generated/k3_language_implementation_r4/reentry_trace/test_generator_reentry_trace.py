import re

import reasoning_core.tasks.generated.k3_language_implementation_r4.reentry_trace.generator_reentry_trace as m


def _ex(level):
    import random
    random.seed(level * 991 + 7)
    task = m.ReentryTrace()
    task.config.set_level(level)
    return task.generate_example()


def test_gold_scores_one_all_levels():
    import random
    for level in (0, 1, 3, 6):
        random.seed(100 + level)
        task = m.ReentryTrace()
        task.config.set_level(level)
        for _ in range(5):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0, (level, ex.answer)


def test_garbage_scores_zero():
    ex = _ex(1)
    assert m.ReentryTrace().score_answer("", ex) == 0.0
    assert m.ReentryTrace().score_answer("reajrjrje9595!", ex) == 0.0
    assert m.ReentryTrace().score_answer("import fakemodule", ex) == 0.0


def test_emitted_is_domain_valid():
    ex = _ex(0)
    assert isinstance(ex.metadata.emitted, list)
    assert all(isinstance(v, int) for v in ex.metadata.emitted)
    assert len(ex.metadata.emitted) >= 2


def test_prompt_contains_driver_and_code():
    ex = _ex(2)
    assert "yield from" in ex.prompt
    assert "send" in ex.prompt or "close" in ex.prompt
    assert "Python list of ints" in ex.prompt


def test_metadata_json_roundtrip():
    import json
    ex = _ex(3)
    json.dumps(dict(ex.metadata))
    rt = json.loads(json.dumps(dict(ex.metadata)))
    assert rt["ops"] == ex.metadata.ops


def test_answer_format_matches_prompt():
    ex = _ex(0)
    assert re.fullmatch(r"\[-?\d+(, -?\d+)*\]", ex.answer)


def test_difficulty_changes_structure():
    import random
    random.seed(5)
    t0 = m.ReentryTrace()
    t0.config.set_level(0)
    t6 = m.ReentryTrace()
    t6.config.set_level(6)
    assert t6.config.depth >= t0.config.depth
    assert t6.config.ops_len >= t0.config.ops_len
