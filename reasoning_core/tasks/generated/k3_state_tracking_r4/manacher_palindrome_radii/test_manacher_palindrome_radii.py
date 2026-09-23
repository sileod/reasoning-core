import random

from reasoning_core.tasks.generated.k3_state_tracking_r4.manacher_palindrome_radii.manacher_palindrome_radii import (
    ManacherConfig,
    ManacherPalindromeRadii,
    manacher_radii,
)


def brute_radii(s):
    n = len(s)
    odd = []
    for i in range(n):
        k = 1
        while i - k >= 0 and i + k < n and s[i - k] == s[i + k]:
            k += 1
        odd.append(2 * k - 1)
    even = []
    for i in range(n):
        k = 0
        while i - k - 1 >= 0 and i + k < n and s[i - k - 1] == s[i + k]:
            k += 1
        even.append(2 * k)
    return odd, even


def test_gold_scores_one():
    random.seed(12345)
    task = ManacherPalindromeRadii()
    for _ in range(50):
        e = task.generate_example()
        assert task.score_answer(e.answer, e) == 1.0


def test_gold_roundtrip_matches_bruteforce():
    random.seed(99)
    task = ManacherPalindromeRadii()
    for c in range(2, 10):
        for _ in range(30):
            task.config.set_level(c % 7)
            e = task.generate_example()
            s = e.metadata["string"]
            odd, even = brute_radii(s)
            assert e.metadata["odd"] == odd
            assert e.metadata["even"] == even[:-1]


def test_junk_and_empty_score_zero():
    random.seed(7)
    task = ManacherPalindromeRadii()
    e = task.generate_example()
    assert task.score_answer("", e) == 0.0
    assert task.score_answer("garbage here", e) == 0.0
    assert task.score_answer("1 2", e) == 0.0


def test_answer_domain_nonnegative():
    random.seed(42)
    task = ManacherPalindromeRadii()
    for level in range(7):
        task.config.set_level(level)
        e = task.generate_example()
        n = e.metadata["centers"]
        assert len(e.answer.split()) == 2 * n - 1
        for v in e.answer.split():
            assert int(v) >= 1 or v == "0"


def test_difficulty_changes_length():
    random.seed(3)
    task = ManacherPalindromeRadii()
    base = task.config.length
    task.config.set_level(3)
    assert task.config.length > base
