import random

import pytest

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_novel_composition_r1.toy_spn_cipher_rounds.toy_spn_cipher_rounds import (
    ToySPNCipherRounds,
    _round_fn,
    SBOX_A,
    SBOX_B,
)


@pytest.fixture
def task():
    return ToySPNCipherRounds()


def test_example_scores_one(task):
    ex = task.generate_example()
    assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_in_domain(task):
    for _ in range(200):
        ex = task.generate_example()
        a = int(ex.answer)
        assert 0 <= a <= 255


def test_round_fn_known():
    sbox = [0xE, 0x4, 0xD, 0x1, 0x2, 0xF, 0xB, 0x8,
            0x3, 0xA, 0x6, 0xC, 0x5, 0x9, 0x0, 0x7]
    perm = list(range(8))
    # state 0x0F: high=0, low=15. low nibble -> sbox[15]=0x7, high -> sbox[0]=0xE.
    # permuted = high<<4 | low = 0xE7 = 231; key 0 keeps it.
    assert _round_fn(0x0F, 0, sbox, perm) == 231


def test_wrong_answer_not_one(task):
    ex = task.generate_example()
    ok = int(ex.answer)
    wrong = (ok + 1) % 256
    assert task.score_answer(str(wrong), ex) == 0.0


def test_rounds_vary_by_level():
    t0 = ToySPNCipherRounds()
    t0.config.set_level(0)
    c0 = t0.config.rounds
    t6 = ToySPNCipherRounds()
    t6.config.set_level(6)
    assert t6.config.rounds > c0


def test_score_empty_junk(task):
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("abc", ex) == 0.0


def test_reference_roundtrip():
    for _ in range(50):
        t = ToySPNCipherRounds()
        t.config.set_level(random.randrange(7))
        ex = t.generate_entry()
        m = ex.metadata
        assert int(ex.answer) == m["ciphertext"]
        assert 0 <= m["ciphertext"] <= 255
        assert len(m["round_keys"]) == m["rounds"]


def test_sboxes_are_permutations():
    assert sorted(SBOX_A) == list(range(16))
    assert sorted(SBOX_B) == list(range(16))


def test_surface_leak_guarded():
    t = ToySPNCipherRounds()
    t.config.set_level(random.randrange(7))
    ex = t.generate_entry()
    if int(ex.answer) == ex.metadata["plaintext"]:
        return
    assert ex.answer != str(ex.metadata["plaintext"])
