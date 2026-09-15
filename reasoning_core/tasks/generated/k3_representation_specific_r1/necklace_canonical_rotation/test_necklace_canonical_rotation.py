import random
import pytest

from reasoning_core.tasks.generated.k3_representation_specific_r1.necklace_canonical_rotation.necklace_canonical_rotation import (
    NecklaceCanonicalRotation,
    _canonical,
    _verify,
    _is_minimal_period,
    _parse_answer,
)


@pytest.fixture
def task():
    return NecklaceCanonicalRotation()


def test_canonical_known_cases():
    assert _canonical("abab") == ("abab", 0, 2, 2)
    assert _canonical("baba") == ("abab", 1, 2, 2)
    assert _canonical("abc") == ("abc", 0, 3, 1)
    assert _canonical("bca") == ("abc", 2, 3, 1)
    assert _canonical("aaaa") == ("aaaa", 0, 1, 4)


def test_verify_and_recompute_agree():
    for s in ["abab", "baba", "abc", "aab", "baa", "ab", "ccc", "ababab"]:
        canon, idx, per, order = _canonical(s)
        assert _verify(s, canon, idx, per, order)
        assert _is_minimal_period(s, per)
        assert per * order == len(s)


def test_gold_scores_one(task):
    for _ in range(50):
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0
        assert _verify(ex.metadata["word"], ex.metadata["canonical"],
                       ex.metadata["index"], ex.metadata["period"], ex.metadata["order"])


def test_wrong_and_junk_do_not_score(task):
    for _ in range(30):
        ex = task.generate_example()
        assert task.score_answer("garbage", ex) == 0.0
        assert task.score_answer("", ex) == 0.0
        assert task.score_answer(ex.answer[:-3], ex) == 0.0
        assert task.score_answer("a,1,1,0", ex) == 0.0


def test_levels_change_config(task):
    c0 = task.config.to_dict()
    task.config.set_level(6)
    c6 = task.config.to_dict()
    assert c6 != c0
    assert c6["max_len"] > c0["max_len"]


def test_all_levels_generate(task):
    for level in range(7):
        ex = task.generate_example(level=level)
        assert task.score_answer(ex.answer, ex) == 1.0


def test_answer_domain(task):
    for _ in range(200):
        ex = task.generate_example()
        p = _parse_answer(ex.answer)
        assert p is not None
        canon, idx, per, order = p
        n = len(ex.metadata["word"])
        assert 0 <= idx < n
        assert 1 <= per <= n
        assert 1 <= order <= n
        assert per * order == n
        assert len(canon) == n


def test_reproducible_under_seed():
    random.seed(3867019559)
    a = [NecklaceCanonicalRotation().generate_example().answer for _ in range(20)]
    random.seed(3867019559)
    b = [NecklaceCanonicalRotation().generate_example().answer for _ in range(20)]
    assert a == b
