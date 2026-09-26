from reasoning_core.tasks.generated.wave8.set_associative_cache.set_associative_cache import (
    SetAssociativeCache,
    _compute_gold,
)


def test_gold_scores_one():
    task = SetAssociativeCache()
    entry = task.generate_example()
    assert task.score_answer(entry.answer, entry) == 1.0


def test_answer_matches_gold():
    task = SetAssociativeCache()
    entry = task.generate_example()
    md = entry.metadata
    accesses = list(md["accesses"])
    policy = 0 if md["policy"] == "LRU" else 1
    hit, s, w = _compute_gold(md["n_sets"], md["n_ways"], accesses, policy)
    exp = f"{'HIT' if hit else 'MISS'} set {s} way {w}"
    assert entry.answer == exp


def test_junk_not_one():
    task = SetAssociativeCache()
    entry = task.generate_example()
    assert task.score_answer("", entry) < 1.0
    assert task.score_answer("garbage", entry) < 1.0
    assert task.score_answer("MISS set 99 way 99", entry) < 1.0


def test_levels_work():
    for level in (0, 1, 2, 3, 4, 5, 6):
        cfg = SetAssociativeCache.config_cls()
        cfg.set_level(level)
        task = SetAssociativeCache(config=cfg)
        for _ in range(10):
            entry = task.generate_example()
            assert task.score_answer(entry.answer, entry) == 1.0


def test_validate():
    SetAssociativeCache().validate()


def test_answer_space_varied():
    seen = set()
    for level in (0, 3, 6):
        cfg = SetAssociativeCache.config_cls()
        cfg.set_level(level)
        task = SetAssociativeCache(config=cfg)
        for _ in range(100):
            seen.add(task.generate_example().answer)
    assert len(seen) > 30


def test_both_hit_and_miss():
    hits = misses = 0
    for level in (0, 3, 6):
        cfg = SetAssociativeCache.config_cls()
        cfg.set_level(level)
        task = SetAssociativeCache(config=cfg)
        for _ in range(100):
            entry = task.generate_example()
            if entry.answer.startswith("HIT"):
                hits += 1
            else:
                misses += 1
    assert hits > 0 and misses > 0


def test_wrong_format_not_one():
    task = SetAssociativeCache()
    entry = task.generate_example()
    assert task.score_answer("HIT set 0 way 0 extra", entry) < 1.0
    assert task.score_answer("hit set 0 way 0", entry) < 1.0


def test_a_way_is_the_slot_filled_lowest_empty_first():
    from reasoning_core.tasks.generated.wave8.set_associative_cache.set_associative_cache import (
        _compute_gold)
    # v1 said "way 1" here (block 21 mod 5); 14 and 0 hold ways 0 and 1, so 21 fills way 2.
    assert _compute_gold(7, 5, [14, 16, 25, 24, 12, 11, 16, 0, 26, 24, 3, 22, 21], 1) == (0, 0, 2)
    assert _compute_gold(1, 2, [0, 1, 0, 2, 0], 0) == (1, 0, 0)   # LRU: the hit kept 0, 1 left
    assert _compute_gold(1, 2, [0, 1, 0, 2, 0], 1) == (0, 0, 1)   # FIFO: 0 left, 1 is next out
