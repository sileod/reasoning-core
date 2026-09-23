"""Tests for pivot_rotation_fixture_building."""

import random

from reasoning_core.tasks.generated.k3_operations_research_r4.pivot_rotation_fixture_building.pivot_rotation_fixture_building import (
    _breaks,
    _homeaway,
    _normal_pairs,
    _round_pairings,
    _score_answer,
    PivotRotationFixtureBuilding,
)


def _all_pairs_seen_once(num_teams, mirror):
    seen = set()
    rounds = num_teams - 1
    if mirror:
        rounds = 2 * (num_teams - 1)
    for r in range(rounds):
        for (h, a) in _round_pairings(num_teams, r, mirror):
            key = tuple(sorted((h, a)))
            assert h != a
            assert a in range(num_teams)
            seen.add(key)
    expected = num_teams * (num_teams - 1) // 2
    assert len(seen) == expected, (num_teams, mirror, len(seen), expected)


def test_schedule_is_round_robin():
    for n in (4, 6, 8, 10, 12):
        _all_pairs_seen_once(n, False)


def test_schedule_mirror_plays_each_pair_twice():
    for n in (4, 6, 8):
        seen = {}
        rounds = 2 * (n - 1)
        for r in range(rounds):
            for (h, a) in _round_pairings(n, r, True):
                key = tuple(sorted((h, a)))
                seen[key] = seen.get(key, 0) + 1
        assert all(v == 2 for v in seen.values()), seen
        assert len(seen) == n * (n - 1) // 2


def test_homeaway_alphabet_and_length():
    for n in (4, 6, 8, 12):
        for mirror in (False, True):
            length = 2 * (n - 1) if mirror else (n - 1)
            for t in range(n):
                s = _homeaway(n, t, mirror)
                assert len(s) == length
                assert set(s) <= {'H', 'A'}
                if mirror:
                    half = length // 2
                    comp = ''.join('H' if c == 'A' else 'A' for c in s[:half])
                    assert s[half:] == comp


def test_mirror_breaks_formula():
    for n in (4, 6, 8):
        single = _breaks(n, False)
        double = _breaks(n, True)
        boundary = sum(1 for t in range(n) if _homeaway(n, t, False)[-1] != _homeaway(n, t, False)[0])
        assert double == 2 * single + boundary, (n, single, double, boundary)
        assert double >= 0


def test_score_answer_gold_and_junk():
    task = PivotRotationFixtureBuilding()

    def run(level):
        task.config.set_level(level)
        for _ in range(30):
            e = task.generate_example()
            assert _score_answer(e.answer, e) == 1.0
            assert _score_answer('', e) < 1.0
            assert _score_answer('junk', e) < 1.0
            assert _score_answer('0@1@2||3', e) < 1.0

    for level in (0, 2, 5):
        run(level)


def test_score_answer_accepts_pairing_permutation():
    task = PivotRotationFixtureBuilding()
    task.config.set_level(0)
    for _ in range(20):
        e = task.generate_example()
        parts = e.answer.split('|')
        toks = parts[0].split(';')
        random.shuffle(toks)
        variant = ';'.join(toks) + '|' + parts[1] + '|' + parts[2]
        assert _score_answer(variant, e) == 1.0


def test_score_answer_rejects_wrong_homeaway_or_breaks():
    task = PivotRotationFixtureBuilding()
    task.config.set_level(0)
    e = task.generate_example()
    parts = e.answer.split('|')
    bad_ha = ('H' if parts[1][0] == 'A' else 'A') + parts[1][1:]
    assert _score_answer(parts[0] + '|' + bad_ha + '|' + parts[2], e) < 1.0
    bad_count = '0' if parts[2] != '0' else '1'
    assert _score_answer(parts[0] + '|' + parts[1] + '|' + bad_count, e) < 1.0


def test_config_difficulty_scales():
    task = PivotRotationFixtureBuilding()
    task.config.set_level(0)
    n0 = task.config.num_teams
    task.config.set_level(6)
    n6 = task.config.num_teams
    assert n6 > n0
    assert n6 % 2 == 0
