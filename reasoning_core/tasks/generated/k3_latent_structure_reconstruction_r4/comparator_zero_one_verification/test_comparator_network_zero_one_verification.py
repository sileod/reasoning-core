import random
from itertools import product

from reasoning_core.tasks.generated.k3_latent_structure_reconstruction_r4.comparator_zero_one_verification.comparator_network_zero_one_verification import (
    ComparatorZeroOneVerification,
    _sorts_all,
)


def test_generate_and_score():
    t = ComparatorZeroOneVerification()
    for level in range(7):
        t.config.set_level(level)
        for _ in range(20):
            x = t.generate_example()
            assert t.score_answer(x.answer, x) == 1.0
            if x.metadata["answer"] == "YES":
                assert _sorts_all(x.metadata["network"], x.metadata["wires"])[0]
            else:
                assert not _sorts_all(x.metadata["network"], x.metadata["wires"])[0]


def test_difficulty_changes_config():
    t = ComparatorZeroOneVerification()
    t.config.set_level(0)
    w0 = t.config.wires
    c0 = t.config.comparators
    t.config.set_level(6)
    assert (t.config.wires, t.config.comparators) != (w0, c0)


def test_balanced_labels():
    random.seed(1)
    t = ComparatorZeroOneVerification()
    t.config.set_level(3)
    ys = 0
    ns = 0
    for _ in range(200):
        x = t.generate_example()
        if x.metadata["answer"] == "YES":
            ys += 1
        else:
            ns += 1
    assert 40 <= ys <= 160
    assert 40 <= ns <= 160


def test_sorts_all_helper():
    net = [(0, 1)]
    assert _sorts_all(net, 2)[0]
    net2 = [(1, 0)]
    ok, word = _sorts_all(net2, 2)
    assert not ok
    assert tuple(sorted(word)) == (0, 1) or word in [(1, 0)]


def test_junk_and_empty():
    t = ComparatorZeroOneVerification()
    x = t.generate_example()
    assert t.score_answer("", x) < 1.0
    assert t.score_answer("garbage", x) < 1.0
