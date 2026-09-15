import importlib.util
from pathlib import Path

import pytest

_HERE = Path(__file__).parent
_MODULE = _HERE / "nonstandard_base_translation.py"

_spec = importlib.util.spec_from_file_location("nonstandard_base_translation_task", _MODULE)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

NonstandardBaseTranslation = _mod.NonstandardBaseTranslation
_encode_answer = _mod._encode_answer
decimal_to_base_n = _mod.decimal_to_base_n
from_balanced_ternary = _mod.from_balanced_ternary
from_digits = _mod.from_digits
from_naf = _mod.from_naf
to_balanced_ternary = _mod.to_balanced_ternary
to_naf = _mod.to_naf


def test_roundtrip_negabinary():
    for v in list(range(-200, 201)):
        digits = decimal_to_base_n(v, -2)
        assert from_digits(digits, -2) == v


def test_roundtrip_negadecimal():
    for v in list(range(-200, 201)):
        digits = decimal_to_base_n(v, -10)
        assert from_digits(digits, -10) == v


def test_roundtrip_balanced_ternary():
    for v in list(range(-200, 201)):
        digits = to_balanced_ternary(v)
        assert from_balanced_ternary(digits) == v


def test_roundtrip_naf():
    for v in list(range(-200, 201)):
        digits = to_naf(v)
        assert from_naf(digits) == v
        for i in range(len(digits) - 1):
            assert not (digits[i] and digits[i + 1])


def test_naf_non_adjacent_property():
    digits = to_naf(1234567)
    for i in range(len(digits) - 1):
        assert not (digits[i] and digits[i + 1])


def test_known_values():
    assert _encode_answer(5, "balanced ternary") == "1 -1 -1"
    assert _encode_answer(0, "NAF") == "0"
    assert from_naf(to_naf(-12345)) == -12345


def test_gold_scores():
    task = NonstandardBaseTranslation()
    for level in range(7):
        task.config.set_level(level)
        for _ in range(50):
            entry = task.generate_entry()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_gold_validates_domain():
    task = NonstandardBaseTranslation()
    for _ in range(200):
        entry = task.generate_entry()
        value = entry.metadata["value"]
        if entry.metadata["base"] == "NAF":
            assert from_naf(to_naf(value)) == value
