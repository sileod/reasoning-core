import random

from reasoning_core.tasks.generated.k3_parsing_and_agreement_r1.vowel_harmony_spreading.vowel_harmony_spreading import (
    VowelHarmonySpreading,
    VowelHarmonyConfig,
    compute,
    melody_string,
)


def test_roundtrip_dominant():
    random.seed(7)
    t = VowelHarmonySpreading()
    for _ in range(50):
        e = t.generate_example()
        assert t.score_answer(e.answer, e) == 1.0
        assert t.score_answer("", e) < 1.0
        assert t.score_answer("garbage", e) < 1.0


def test_compute_deterministic_known():
    surf, _ = compute(
        "root",
        "101",
        [[0, 0, 0], [1, 1, 1]],
        [["U", "U", "U"], ["U", "U", "U"]],
    )
    assert surf == [["1", "0", "1"], ["1", "0", "1"]]


def test_blocker_stops_spread():
    surf, dish = compute(
        "root", "111", [[0, 0, 0]], [["B", "B", "B"]]
    )
    assert surf == [["X", "X", "X"]]
    assert dish is False


def test_revert_is_disharmonic():
    surf, dish = compute(
        "root", "111", [[0, 0, 0], [0, 0, 0]],
        [["B", "B", "B"], ["U", "U", "U"]],
    )
    assert surf[0] == ["X", "X", "X"]
    assert surf[1] == ["0", "0", "0"]
    assert dish is True


def test_neutral_transparent():
    surf, dish = compute(
        "root", "111", [[0, 0, 0], [0, 0, 0]],
        [["N", "N", "N"], ["U", "U", "U"]],
    )
    assert surf[0] == ["0", "0", "0"]
    assert surf[1] == ["1", "1", "1"]
    assert dish is False


def test_dominant_never_X():
    t = VowelHarmonySpreading()
    random.seed(3)
    for _ in range(100):
        e = t.generate_example()
        if e.metadata["system"] == "dominant":
            assert "X" not in e.answer
            assert e.answer != "disharmony"


def test_difficulty_changes():
    c = VowelHarmonyConfig()
    c.set_level(0)
    assert c.num_affixes == 2
    c.set_level(6)
    assert c.num_affixes == 8


def test_metadata_json_safe():
    import json

    random.seed(11)
    t = VowelHarmonySpreading()
    e = t.generate_example()
    json.dumps(e.metadata)


def test_disagree_sanskrit_exact_roundtrip_all_levels():
    t = VowelHarmonySpreading()
    for level in (0, 1, 2, 3, 4, 5, 6):
        t.config.set_level(level)
        random.seed(100 + level)
        for _ in range(20):
            e = t.generate_example()
            assert t.score_answer(e.answer, e) == 1.0
            assert t.score_answer("", e) < 1.0
            raw = e.answer
            gold = "disharmony" if raw == "disharmony" else melody_string(
                [[c for c in tkn] for tkn in
                 [tkn.split("-") for tkn in raw.split(" | ")]])
            assert t.score_answer(gold, e) == 1.0


def test_disharmony_present_and_not_constant():
    t = VowelHarmonySpreading()
    random.seed(99)
    answers = {}
    dish = 0
    root = 0
    for _ in range(200):
        e = t.generate_example()
        answers[e.answer] = answers.get(e.answer, 0) + 1
        if e.metadata["system"] == "root":
            root += 1
            if e.metadata["disharmonic"]:
                dish += 1
    assert len(answers) > 20
    assert 0.05 < dish / root < 0.9


def test_backness_order_x_only_root_blocked():
    t = VowelHarmonySpreading()
    random.seed(5)
    for _ in range(80):
        e = t.generate_example()
        if e.answer != "disharmony":
            affixes = e.answer.split(" | ")
            assert all(len(a.split("-")) == 3 for a in affixes)
            assert all(c in "01X" for a in affixes for c in a.split("-"))
