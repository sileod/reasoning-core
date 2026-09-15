from .debruijn_scope_translation import (
    DeBruijnScopeTranslationV1,
    _db_to_named,
    _has_bound,
    _named_to_db,
    _parse_db,
)


def test_gold_scores_one_at_multiple_levels():
    task = DeBruijnScopeTranslationV1()
    for level in (0, 1, 2, 3, 6):
        task.config.set_level(level)
        ex = task.generate_example()
        assert task.score_answer(ex.answer, ex) == 1.0, level


def test_difficulty_changes_config():
    task = DeBruijnScopeTranslationV1()
    task.config.set_level(0)
    base = task.config.max_depth
    task.config.set_level(6)
    assert task.config.max_depth > base


def test_junk_and_empty_score_zero():
    task = DeBruijnScopeTranslationV1()
    ex = task.generate_example()
    assert task.score_answer("", ex) == 0.0
    assert task.score_answer("zzz", ex) == 0.0
    assert task.score_answer("# # ( )", ex) == 0.0


def test_round_trip_is_structural_fixpoint():
    task = DeBruijnScopeTranslationV1()
    task.config.set_level(5)
    for _ in range(50):
        tree = _gen_fixture()
        if tree is None:
            continue
        db = _named_to_db(tree)
        if not db or not _has_bound(db):
            continue
        named2 = _db_to_named(_parse_db(db))
        assert _named_to_db(named2) == db


def _gen_fixture():
    from .debruijn_scope_translation import _gen_term
    for _ in range(200):
        t = _gen_term(4, [], list("abc"), 0.5)
        if not _has_bound(_named_to_db(t)):
            continue
        return t
    return None


def test_balance_of_free_and_bound():
    task = DeBruijnScopeTranslationV1()
    task.config.set_level(2)
    seen_free = False
    seen_bound_only = False
    for _ in range(40):
        ex = task.generate_example()
        db = ex.answer
        if "#" in db:
            seen_free = True
        else:
            seen_bound_only = True
    assert seen_free and seen_bound_only
