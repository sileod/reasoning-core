from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.lyndon_factorization_duval.lyndon_factorization_duval import (
    LyndonFactorizationDuval,
    LyndonFactorizationConfig,
    _duval,
    _is_lyndon,
    _verify_factors,
)


def test_round_trip():
    task = LyndonFactorizationDuval()
    x = task.generate_example()
    assert task.score_answer(x.answer, x) == 1.0


def test_gold_scores_one_all_levels():
    task = LyndonFactorizationDuval()
    for level in range(7):
        cfg = LyndonFactorizationConfig()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(20):
            x = task.generate_example()
            assert task.score_answer(x.answer, x) == 1.0


def test_garbage_scores_zero():
    task = LyndonFactorizationDuval()
    x = task.generate_example()
    assert task.score_answer("", x) == 0.0
    assert task.score_answer("junk", x) == 0.0


def test_duval_matches_verifier():
    letters = "abc"
    import random
    for _ in range(300):
        n = random.randint(1, 18)
        word = "".join(random.choice(letters) for _ in range(n))
        factors = _duval(word)
        assert _verify_factors(word, factors), (word, factors)
        assert "".join(factors) == word


def test_known_factorizations():
    assert _duval("a") == ["a"]
    assert _verify_factors("aaaa", _duval("aaaa"))
    assert _verify_factors("abab", _duval("abab"))
    assert _verify_factors("baab", _duval("baab"))


def test_is_lyndon():
    assert _is_lyndon("a")
    assert _is_lyndon("ab")
    assert not _is_lyndon("ba")
    assert not _is_lyndon("abab")
    assert _is_lyndon("aab")


def test_wrong_order_scores_zero():
    task = LyndonFactorizationDuval()
    x = task.generate_example()
    factors = x.metadata.factors
    if len(factors) >= 2:
        reversed_order = " ".join(factors[::-1])
        assert task.score_answer(reversed_order, x) == 0.0


def test_difficulty_changes():
    cfg0 = LyndonFactorizationConfig()
    cfg6 = LyndonFactorizationConfig()
    cfg0.set_level(0)
    cfg6.set_level(6)
    assert cfg6.max_len > cfg0.max_len
    assert cfg6.alphabet_size >= cfg0.alphabet_size


def test_answer_varies():
    task = LyndonFactorizationDuval()
    answers = set()
    for _ in range(80):
        x = task.generate_example()
        answers.add(x.answer)
    assert len(answers) >= 30


def test_metadata_json_serializable():
    import json
    task = LyndonFactorizationDuval()
    x = task.generate_example()
    json.dumps(x.to_dict())
