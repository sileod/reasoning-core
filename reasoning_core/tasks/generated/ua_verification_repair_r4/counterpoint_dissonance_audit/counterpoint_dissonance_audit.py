import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task

TASK_META = {'parent_source_id': None,
 'idea': 'counterpoint_dissonance_audit (variant 1 of 3)',
 'hypothesis': 'P003',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_verification_repair_r4/counterpoint_dissonance_audit',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 2267388306,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}

CONSONANT = frozenset({0, 3, 4, 7, 8, 9})
LABELS = ('PLAIN', 'SUS', 'PT', 'NT')


def _make_token(label, interval, accent):
    return ':'.join((label, str(int(interval)), accent))


def _licenses_dissonance(label, accent):
    if label == 'SUS':
        return accent == 'accented'
    if label in ('PT', 'NT'):
        return accent == 'unaccented'
    return False


def _events_valid(events):
    for token in events:
        label, raw_iv, accent = token.split(':')
        interval = int(raw_iv)
        if interval in CONSONANT:
            continue
        if not _licenses_dissonance(label, accent):
            return False
    return True


def _first_violation(events):
    for token in events:
        label, raw_iv, accent = token.split(':')
        interval = int(raw_iv)
        if interval in CONSONANT:
            continue
        if not _licenses_dissonance(label, accent):
            return token
    return 'OK'


def _make_valid_event():
    interval = random.randrange(12)
    if interval in CONSONANT:
        label = random.choice(LABELS)
        accent = random.choice(('accented', 'unaccented'))
        return _make_token(label, interval, accent)
    if random.random() < 0.5:
        return _make_token('SUS', interval, 'accented')
    return _make_token(random.choice(('PT', 'NT')), interval, 'unaccented')


def _make_invalid_event():
    interval = random.choice((1, 2, 5, 6, 10, 11))
    choice = random.choice(('sus_u', 'turn_a', 'plain'))
    if choice == 'sus_u':
        return _make_token('SUS', interval, 'unaccented')
    if choice == 'turn_a':
        return _make_token(random.choice(('PT', 'NT')), interval, 'accented')
    return _make_token('PLAIN', interval, random.choice(('accented', 'unaccented')))


def _valid_mutations(events, n_bad, indices):
    """Patch up only the non-planted events (those not in indices) to be valid."""
    out = list(events)
    for i in range(len(out)):
        if i in indices:
            continue
        out[i] = _make_valid_event()
    return out


@dataclass
class CounterpointConfig(Config):
    count: int = 3
    ok_prob: float = 0.35

    def apply_difficulty(self, level):
        self.count = 3 + level * 2
        self.ok_prob = 0.12


class CounterpointDissonanceAudit(Task):
    summary = ("Verify dissonance licenses across accented and unaccented intervals, suspensions, "
               "passing tones, and neighboring tones; return the first unsupported event token or "
               "OK when every stated rule is satisfied.")
    design_choice = ("Represent each voice-leading event as a compact token string "
                     "(e.g., 'SUS:4-3:accented') and require the solver to output the first token "
                     "that violates a stated dissonance rule, or 'OK' if all pass.")
    config_cls = CounterpointConfig

    def generate_entry(self):
        count = self.config.count
        ok_prob = self.config.ok_prob
        for _ in range(200):
            if random.random() < ok_prob:
                events = [_make_valid_event() for _ in range(count)]
                answer = 'OK'
            else:
                n_bad = random.randint(1, 2)
                indices = sorted(random.sample(range(count), min(n_bad, count)))
                events = [None] * count
                for i in indices:
                    events[i] = _make_invalid_event()
                events = _valid_mutations(events, len(indices), set(indices))
                answer = _first_violation(events)
            if answer != 'OK':
                first = _first_violation(events)
                assert first == answer
                assert events.index(first) >= indices[0]
                assert len(set(events)) > 1 or count == 1
            return Entry(metadata={'events': events, 'answer': answer}, answer=answer)
        raise RuntimeError('failed to build a counterpoint instance')

    def render_prompt(self, metadata):
        events = metadata['events']
        ah = '; '.join(events)
        return (
            "An auditor checks a two-voice counterpoint. Each event records a vertical interval "
            "(in semitones 0..11) between the voices, the beat accent, and the ornamental role. "
            "A dissonant interval, i.e. one of 1,2,5,6,10,11 semitones, is allowed only when its "
            "role licenses it: a suspension (SUS) licenses a dissonance only on an accented beat; "
            "a passing tone (PT) or neighboring tone (NT) licenses a dissonance only on an "
            "unaccented beat. A consonant interval, i.e. one of 0,3,4,7,8,9 semitones, is always "
            "allowed regardless of role or accent. Audit the listed events in order: " + ah +
            ". Give the exact token of the first event whose dissonance is not licensed, or OK if "
            "all are licensed. Answer with the token itself, e.g. SUS:2:accented, or OK."
        )

    def score_answer(self, answer, entry):
        return 1.0 if str(answer).strip() == entry['answer'] else 0.0
