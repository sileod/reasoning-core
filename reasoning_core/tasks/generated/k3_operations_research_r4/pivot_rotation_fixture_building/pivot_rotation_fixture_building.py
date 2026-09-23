"""Pivot-rotation round-robin fixture building.

Schedule an even number of teams into rounds with team 0 fixed as the pivot and the
rest rotated each round (the circle method), assign venues by symmetric position
parity, and optionally mirror the rounds into a double season.  A generator-driven
question asks, for one chosen round, for the pairings, for one team's home/away
sequence across the whole season, and for the total break count, as one
delimiter-separated answer line.
"""

import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

design_choice = "For a given round index, output the pairings as a canonical list of 'TeamA@TeamB' strings, plus a home/away sequence for a specified team and its break count, all in a fixed delimiter-separated string."

TASK_META = {'parent_source_id': None,
             'idea': 'pivot_rotation_fixture_building (variant 2 of 3)',
             'hypothesis': 'P010',
             'changes': 'new task in '
                        'reasoning_core/tasks/generated/k3_operations_research_r4/pivot_rotation_fixture_building',
             'generation': {'provider_name': 'albert',
                            'model_name': 'deepseek-v4-flash',
                            'harness_name': 'opencode',
                            'harness_version': '1.18.32',
                            'agent_name': 'task-search-worker',
                            'settings': {'variant': None,
                                         'requested_seed': 1211525277,
                                         'seed_forwarded': True,
                                         'temperature': None,
                                         'top_p': None,
                                         'pure': True,
                                         'max_steps': 56,
                                         'timeout_seconds': 1800,
                                         'sandbox': {'name': 'bubblewrap',
                                                     'version': 'bubblewrap 0.8.0'}}}}


def _round_order(num_teams, r):
    """Team-index ordering at round r of the circle method with team 0 fixed.

    Team 0 stays at index 0 (the pivot); indices 1..n-1 are rotated right by one
    each round.  Round r in 0..n-2.
    """
    arr = list(range(num_teams))
    for _ in range(r % (num_teams - 1)):
        arr = [arr[0]] + arr[-1:] + arr[1:-1]
    return arr


def _normal_pairs(num_teams, r):
    """Canonical (home, away) pairings for round r of the single season."""
    arr = _round_order(num_teams, r)
    half = num_teams // 2
    pairs = []
    for i in range(half):
        pairs.append((arr[i], arr[num_teams - 1 - i]))
    return pairs


def _round_pairings(num_teams, r, mirror):
    """(home, away) pairings for round r, handling the mirrored return leg."""
    base = num_teams - 1
    if mirror and r >= base:
        return [(a, h) for (h, a) in _normal_pairs(num_teams, r - base)]
    return _normal_pairs(num_teams, r)


def _single_homeaway(num_teams, t):
    """Home/away string for team t over the single season's rounds."""
    half = num_teams // 2
    out = []
    for r in range(num_teams - 1):
        arr = _round_order(num_teams, r)
        out.append('H' if arr.index(t) < half else 'A')
    return ''.join(out)


def _homeaway(num_teams, t, mirror):
    single = _single_homeaway(num_teams, t)
    if not mirror:
        return single
    comp = ''.join('H' if c == 'A' else 'A' for c in single)
    return single + comp


def _single_breaks(num_teams):
    seqs = [_single_homeaway(num_teams, t) for t in range(num_teams)]
    total = 0
    for r in range(1, num_teams - 1):
        for s in seqs:
            if s[r] == s[r - 1]:
                total += 1
    return total


def _breaks(num_teams, mirror):
    single = _single_breaks(num_teams)
    if not mirror:
        return single
    boundary = 0
    for t in range(num_teams):
        s = _single_homeaway(num_teams, t)
        if s[-1] != s[0]:
            boundary += 1
    return 2 * single + boundary


def _pairings_ok(candidate, gold):
    """Candidate round pairings match the gold as a set of directed Home@Away."""
    def parse(seg):
        if not seg:
            return set()
        out = set()
        for tok in seg.split(';'):
            left, _, right = tok.partition('@')
            if not left or not right:
                return None
            out.add((left.strip(), right.strip()))
        return out
    c = parse(candidate)
    g = parse(gold)
    if c is None or g is None:
        return False
    return c == g


def _score_answer(answer, entry):
    gold = str(entry['answer']).strip()
    a = str(answer).strip()
    if a == gold:
        return 1.0
    try:
        apart = a.split('|')
        gpart = gold.split('|')
        if len(apart) != 3 or len(gpart) != 3:
            return 0.0
        if not _pairings_ok(apart[0], gpart[0]):
            return 0.0
        if apart[1] != gpart[1]:
            return 0.0
        if apart[2] != gpart[2]:
            return 0.0
        return 1.0
    except Exception:
        return 0.0


@dataclass
class PivotRotationConfig(Config):
    num_teams: int = 8
    mirror_prob: float = 0.2

    def apply_difficulty(self, level):
        self.num_teams = 8 + 2 * level
        self.mirror_prob = min(0.2 + 0.12 * level, 0.9)


class PivotRotationFixtureBuilding(Task):
    summary = ("Rotate all but one team around a fixed pivot to emit round pairings, "
               "set venues by position parity, optionally mirror rounds for a double "
               "season; answers are a round's pairings, a team's home/away string, and "
               "break count.")
    config_cls = PivotRotationConfig

    def generate_entry(self):
        n = self.config.num_teams
        mirror = random.random() < self.config.mirror_prob
        base = n - 1
        num_rounds = 2 * base if mirror else base
        r = random.randrange(0, num_rounds)
        t = random.randrange(0, n)

        pairs = _round_pairings(n, r, mirror)
        homeaway = _homeaway(n, t, mirror)
        breaks = _breaks(n, mirror)

        pairings_str = ';'.join('%d@%d' % (h, a) for (h, a) in pairs)
        answer = '%s|%s|%d' % (pairings_str, homeaway, breaks)

        assert len(homeaway) == num_rounds, 'home/away length mismatch'
        assert all(c in 'HA' for c in homeaway), 'home/away alphabet'
        assert isinstance(breaks, int) and breaks >= 0, 'break count domain'
        assert len(pairs) == n // 2, 'pairing count'
        seen = set()
        for (h, a) in pairs:
            assert h != a and h not in seen and a not in seen, 'bad pairing'
            seen.add(h)
            seen.add(a)
        assert seen == set(range(n)), 'pairings must cover every team'

        cot = ('round %d of %d with mirror=%s; pairings %s; team %d home/away %s; '
               'breaks %d' % (r, num_rounds, mirror, pairings_str, t, homeaway, breaks))
        metadata = {
            'num_teams': n,
            'mirror': mirror,
            'num_rounds': num_rounds,
            'round_index': r,
            'team': t,
            'pairings_str': pairings_str,
            'homeaway': homeaway,
            'breaks': breaks,
            'pivot': 0,
            'cot': cot,
        }
        return Entry(metadata=metadata, answer=answer)

    def balancing_key(self, entry):
        m = entry.metadata
        return '%s:%s:%s:%s' % (
            m['num_teams'], m['mirror'], m['round_index'], m['team'])

    def render_prompt(self, metadata):
        n = metadata['num_teams']
        half = n // 2
        if metadata['mirror']:
            rng = 'The season is a double season: the %d basic rounds are played, then mirrored with each team\'s home and away swapped.' % (n - 1)
        else:
            rng = 'The season is a single round-robin of %d rounds.' % (n - 1)
        return (
            'A round-robin tournament schedules games among %d teams numbered 0..%d. '
            'The circle (pivot) method with team 0 as the fixed pivot produces the '
            'schedule: in every round the other teams are arranged around team 0 and '
            'rotated each round, and the teams at symmetric positions play -- for i '
            'from 0 to %d, the team at position i is home against the team at position '
            '%d (away). %s '
            'Round indexes are 0-based. '
            'For round %d, list the pairings as Home@Away in position order, separated '
            'by ";". Also give team %d\'s home/away string over all rounds as a sequence '
            'of H (home) and A (away) letters, in round order. Also give the total break '
            'count: a break is when a team occupies the same venue (home or away) in two '
            'consecutive rounds, counted over every team and every pair of consecutive '
            'rounds. '
            'Answer with exactly one line of the form pairings|homeaway|breakcount, e.g. '
            '0@5;1@4;2@3|AHHA|5.'
            % (n, n - 1, half - 1, n - 1 - half + 1, rng, metadata['round_index'],
               metadata['team'])
        )

    def score_answer(self, answer, entry):
        return _score_answer(answer, entry)
