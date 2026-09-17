import itertools
import json
import random

import pytest

from reasoning_core.tasks.generated.k3_controlled_nli_r1.weight_sensitive_stress_parse import (
    weight_sensitive_stress_parse as mod,
)

T = mod.WeightSensitiveStressParse


@pytest.mark.parametrize("word,expected", [
    ("tikantra", ["ti", "kan", "tra"]),
    ("aktio", ["ak", "ti", "o"]),
    ("kae", ["kae"]),
    ("kea", ["ke", "a"]),
    ("kaei", ["kae", "i"]),
    ("kieau", ["ki", "e", "au"]),
    ("antlaf", ["an", "tlaf"]),
    ("astmra", ["as", "tmra"]),
    ("anntta", ["annt", "ta"]),
    ("aeoi", ["ae", "oi"]),
])
def test_manual_syllabification(word, expected):
    assert mod.parse_syllables(word) == expected


def test_exhaustive_consonant_boundaries():
    for length in range(5):
        for letters in itertools.product("tml", repeat=length):
            run = "".join(letters)
            allowed = [i for i in range(length + 1)
                       if all(mod.SON[run[j]] < mod.SON[run[j + 1]]
                              for j in range(i, length - 1))]
            cut = min(allowed)
            assert mod.parse_syllables("a" + run + "a") == ["a" + run[:cut], run[cut:] + "a"]


def test_exhaustive_vowel_runs():
    for length in range(1, 7):
        for letters in itertools.product("aie", repeat=length):
            word = "".join(letters)
            syllables = mod.parse_syllables(word)
            assert "".join(syllables) == word
            remaining = word
            for s in syllables:
                paired = len(remaining) > 1 and mod.VSON[remaining[0]] > mod.VSON[remaining[1]]
                assert len(s) == (2 if paired else 1)
                remaining = remaining[len(s):]


def test_feet_and_heads():
    syllables = ["ka", "mi", "tu"]
    assert mod.build_feet(syllables, "left") == [[0, 1], [2]]
    assert mod.build_feet(syllables, "right") == [[0], [1, 2]]
    feet = mod.build_feet(syllables, "left")
    assert mod.footed_parse_answer(syllables, feet, "left") == "'ka.mi-'tu"
    assert mod.footed_parse_answer(syllables, feet, "right") == "ka.'mi-'tu"
    assert mod.build_feet(["ka", "min", "tu", "la"], "left") == [[0], [1], [2, 3]]
    assert mod.build_feet(["kae", "mi", "tu"], "right") == [[0], [1, 2]]


def test_all_weight_patterns():
    for n in range(1, 8):
        for heavy in itertools.product((False, True), repeat=n):
            syllables = ["kan" if h else "ka" for h in heavy]
            for direction in ("left", "right"):
                order = list(range(n))[::1 if direction == "left" else -1]
                expected = []
                while order:
                    j = order.pop(0)
                    foot = [j]
                    if not heavy[j] and order and not heavy[order[0]]:
                        foot.append(order.pop(0))
                    expected.append(sorted(foot))
                assert mod.build_feet(syllables, direction) == sorted(expected)


def test_generated_gold_and_semantics():
    random.seed(1743)
    for level in (0, 2, 3, 5, 6):
        task = T()
        task.config.set_level(level)
        seen = set()
        modes = set()
        for _ in range(100):
            entry = task.generate_entry()
            m = entry.metadata
            json.dumps(m)
            seen.add(entry.answer)
            modes.add(m["mode"])
            assert task.score_answer(entry.answer, entry) == 1.0
            for junk in ("", "junk", None, [], "-1"):
                assert task.score_answer(junk, entry) == 0.0
            assert "".join(m["syllables"]) == m["word"]
            marked = mod.footed_parse_answer(m["syllables"], m["feet"], m["headedness"])
            stressed = [i + 1 for i, s in enumerate(marked.replace("-", ".").split("."))
                        if s.startswith("'")]
            if m["mode"] == "stress":
                assert int(entry.answer) == stressed[0 if m["edge"] == "left" else -1]
            elif m["mode"] == "clash":
                clashes = [i for i in stressed if i + 1 in stressed]
                assert entry.answer == (str(min(clashes)) if clashes else "none")
            else:
                assert entry.answer == marked
        assert len(seen) > 20
        assert modes == {"stress", "parse", "clash"}


def test_verifier_rejects_incorrect_analyses():
    with pytest.raises(AssertionError):
        mod.verify_analysis("aktio", ["a", "kti", "o"], [[0, 1], [2]], [0, 2], "left", "left")
    with pytest.raises(AssertionError):
        mod.verify_analysis("kae", ["ka", "e"], [[0, 1]], [0], "left", "left")
    with pytest.raises(AssertionError):
        mod.verify_analysis("kamintu", ["ka", "min", "tu"], [[0, 1], [2]], [0, 2], "left", "left")


def test_sonority_changes_feet_not_just_segment_count():
    closed = mod.parse_syllables("aktami")
    rising = mod.parse_syllables("atrami")
    assert closed == ["ak", "ta", "mi"]
    assert rising == ["a", "tra", "mi"]
    assert mod.build_feet(closed, "left") == [[0], [1, 2]]
    assert mod.build_feet(rising, "left") == [[0, 1], [2]]
    diphthong = mod.parse_syllables("kaemi")
    hiatus = mod.parse_syllables("keami")
    assert diphthong == ["kae", "mi"]
    assert hiatus == ["ke", "a", "mi"]
    assert mod.build_feet(diphthong, "left") == [[0], [1]]
    assert mod.build_feet(hiatus, "left") == [[0, 1], [2]]


def test_valid_analysis_and_incorrect_stress():
    mod.verify_analysis("katami", ["ka", "ta", "mi"], [[0, 1], [2]], [1, 2], "left", "right")
    with pytest.raises(AssertionError):
        mod.verify_analysis("katami", ["ka", "ta", "mi"], [[0, 1], [2]], [0, 2], "left", "right")
    with pytest.raises(AssertionError):
        mod.verify_analysis("katami", ["ka", "ta", "mi"], [[0], [1], [2]], [0, 1, 2], "left", "right")


def test_scorer_uses_no_self():
    class Mock:
        def __getattribute__(self, name):
            raise AssertionError(name)

    entry = T().generate_entry()
    assert T.score_answer(Mock(), entry.answer, entry) == 1.0
    assert T.score_answer(Mock(), "nonsense", entry) == 0.0


@pytest.mark.parametrize("mode,answer", [("stress", "2"), ("parse", "ka.'ta-'mi"), ("clash", "2")])
def test_hardcoded_answer_formats(mode, answer):
    syllables = mod.parse_syllables("katami")
    feet = mod.build_feet(syllables, "left")
    assert syllables == ["ka", "ta", "mi"]
    assert feet == [[0, 1], [2]]
    assert mod.footed_parse_answer(syllables, feet, "right") == "ka.'ta-'mi"
    metadata = {"word": "katami", "syllables": syllables, "feet": feet, "heads": [1, 2],
                "direction": "left", "headedness": "right", "edge": "left", "mode": mode}
    entry = mod.Entry(metadata=metadata, answer=answer)
    task = T()
    prompt = task.render_prompt(metadata)
    assert "katami" in prompt
    assert task.score_answer(answer, entry) == 1.0
    assert task.score_answer("1", entry) == 0.0
    if mode == "parse":
        assert task.score_answer("'ka.ta-'mi", entry) == 0.0
    elif mode == "clash":
        assert "LEFT member" in prompt
        assert task.score_answer("3", entry) == 0.0
        assert task.score_answer("none", entry) == 0.0


def test_seed_reproducibility_and_prompt():
    for level in (0, 6):
        task = T()
        task.config.set_level(level)
        random.seed(78)
        first = task.generate_entry()
        random.seed(78)
        second = task.generate_entry()
        assert first.answer == second.answer
        assert first.metadata == second.metadata
        prompt = task.render_prompt(first.metadata)
        assert first.metadata["word"] in prompt
        assert "sonority" in prompt
        assert "maximal-onset" in prompt
