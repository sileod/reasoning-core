import pytest

from reasoning_core.template import Config
from reasoning_core.tasks.generated.k3_formal_semantics_r1.tag_adjunction_derivation.tag_adjunction_derivation import (
    TagAdjunctionDerivation,
    TagConfig,
)


@pytest.fixture(scope="module")
def task():
    return TagAdjunctionDerivation()


def test_config_scaling():
    c = TagConfig()
    c.set_level(0)
    lo_min, lo_max, lo_share = c.min_steps, c.max_steps, c.aux_share
    c = TagConfig()
    c.set_level(6)
    assert c.min_steps > lo_min or c.max_steps > lo_max
    assert c.aux_share >= lo_share


def test_generate_roundtrip(task):
    for level in range(7):
        t = TagAdjunctionDerivation()
        t.config.set_level(level)
        for _ in range(50):
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0
            assert isinstance(e.answer, str)
            assert e.metadata["mode"] in ("yield", "action", "validity")


def test_mode_balance(task):
    counts = {"yield": 0, "action": 0, "validity": 0}
    t = TagAdjunctionDerivation()
    t.config.set_level(3)
    for _ in range(600):
        e = t.generate_example()
        counts[e.metadata["mode"]] += 1
    # all three modes should appear reasonably; validity requires >=2 steps
    assert counts["yield"] > 0
    assert counts["action"] > 0
    assert counts["validity"] > 0
    # yield should dominate (it's the only mode possible at 1 step)
    assert counts["yield"] > 100


def test_validity_balance(task):
    t = TagAdjunctionDerivation()
    t.config.set_level(3)
    yes = no = 0
    for _ in range(400):
        e = t.generate_example()
        if e.metadata["mode"] == "validity":
            if e.answer == "yes":
                yes += 1
            else:
                no += 1
    assert yes > 0 and no > 0


def test_scoring_rejects_junk(task):
    t = TagAdjunctionDerivation()
    t.config.set_level(2)
    for _ in range(100):
        e = t.generate_example()
        assert t.score_answer("", e) == 0.0
        assert t.score_answer("zzz", e) == 0.0


def test_default_config_works():
    t = TagAdjunctionDerivation()
    for _ in range(20):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0


def test_action_has_next_operation():
    t = TagAdjunctionDerivation()
    t.config.set_level(3)
    for _ in range(100):
        e = t.generate_example()
        if e.metadata["mode"] == "action":
            assert e.metadata["next_idx"] < len(e.metadata["ops"])


def test_verdict_valid():
    t = TagAdjunctionDerivation()
    t.config.set_level(3)
    for _ in range(100):
        e = t.generate_example()
        if e.metadata["mode"] == "validity":
            assert e.answer in ("yes", "no")


def test_no_hash_in_yield():
    t = TagAdjunctionDerivation()
    t.config.set_level(5)
    for _ in range(200):
        e = t.generate_example()
        if e.metadata["mode"] == "yield":
            assert "#" not in e.answer
            assert e.answer.strip() != ""


def test_yield_recomputable():
    from reasoning_core.tasks.generated.k3_formal_semantics_r1.tag_adjunction_derivation import (
        tag_adjunction_derivation as m,
    )
    t = TagAdjunctionDerivation()
    t.config.set_level(4)
    for _ in range(200):
        e = t.generate_example()
        if e.metadata["mode"] == "yield":
            leaves = m.flat_yield(e.metadata["tree"])
            assert " ".join(leaves) == e.answer
