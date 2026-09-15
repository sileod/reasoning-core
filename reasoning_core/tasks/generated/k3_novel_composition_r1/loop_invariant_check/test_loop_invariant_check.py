import random

import pytest

from reasoning_core.tasks.generated.k3_novel_composition_r1.loop_invariant_check import loop_invariant_check as mod


@pytest.fixture(autouse=True)
def reseed():
    random.seed(2267388306)
    yield
    random.seed()


def test_generate_roundtrip_all_levels():
    for level in range(7):
        t = mod.LoopInvariantCheck()
        t.config.set_level(level)
        t.config.max_retries = 2000
        for _ in range(20):
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0


def test_inducive_construction():
    for _ in range(200):
        c = mod.LoopInvariantCheck()
        c.config.max_retries = 2000
        e = c.generate_example()
        m = e.metadata
        n = m["num_vars"]
        coeffs, const, kind = m["inv_coeffs"], m["inv_const"], m["inv_kind"]
        s = sum(coeffs)
        if kind == "eq":
            assert s == 0 and const == 0
        else:
            assert s <= 0
        assert mod._holds(coeffs, const, kind, m["init"])


def test_witness_is_valid():
    for _ in range(200):
        c = mod.LoopInvariantCheck()
        c.config.max_retries = 2000
        e = c.generate_example()
        m = e.metadata
        n = m["num_vars"]
        w = tuple(m["witness"])
        assert mod._holds(m["inv_coeffs"], m["inv_const"], m["inv_kind"], w)
        assert mod._holds(m["cond_coeffs"], m["cond_const"], m["cond_kind"], w)
        assert not mod._holds(m["post_coeffs"], m["post_const"], m["post_kind"], w)


def test_wrong_answers_fail():
    t = mod.LoopInvariantCheck()
    e = t.generate_example()
    assert t.score_answer("valid", e) == 0.0
    assert t.score_answer("", e) == 0.0
    assert t.score_answer("garbage", e) == 0.0


def test_metadata_json_serializable():
    import json
    t = mod.LoopInvariantCheck()
    e = t.generate_example()
    json.dumps(e.metadata)


def test_valid_answer_format_matches_prompt():
    t = mod.LoopInvariantCheck()
    e = t.generate_example()
    m = e.metadata
    parsed = tuple(int(p) for p in e.answer.split(";"))
    assert parsed == tuple(m["witness"])


def test_answer_varied_at_each_level():
    for level in range(7):
        t = mod.LoopInvariantCheck()
        t.config.set_level(level)
        t.config.max_retries = 2000
        answers = set()
        for _ in range(30):
            answers.add(t.generate_example().answer)
        assert len(answers) >= 5


def test_difficulty_changes_config():
    t = mod.LoopInvariantCheck()
    base = mod.LoopInvariantCheckConfig()
    t.config.set_level(0)
    l0 = (t.config.num_vars, t.config.bound)
    t.config.set_level(6)
    l6 = (t.config.num_vars, t.config.bound)
    assert l0 != l6
    assert l6[0] >= l0[0] and l6[1] > l0[1]


def test_all_levels_generate():
    for level in range(7):
        t = mod.LoopInvariantCheck()
        t.config.set_level(level)
        t.config.max_retries = 2000
        t.generate_example()

