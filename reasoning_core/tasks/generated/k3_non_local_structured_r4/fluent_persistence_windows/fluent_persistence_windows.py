import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class FluentPersistenceWindowsConfig(Config):
    n_fluents: int = 2
    max_t: int = 6
    n_events: int = 4
    max_fluent_per_event: int = 2

    def apply_difficulty(self, level):
        self.n_fluents = 2 + level
        self.max_t = 6 + 3 * level
        self.n_events = 4 + 2 * level


def build_history(config):
    n_fluents = config.n_fluents
    max_t = config.max_t
    n_events = config.n_events
    max_fluent_per_event = config.max_fluent_per_event

    event_times = sorted(random.sample(range(1, max_t + 1), n_events))
    events = []
    for t in event_times:
        k = random.randint(1, max_fluent_per_event)
        mask = random.sample(range(n_fluents), k)
        events.append((t, sorted(mask)))

    running = [False] * n_fluents
    state_at = {}
    for t, mask in events:
        for f in mask:
            running[f] = not running[f]
        state_at[t] = tuple(running)

    return event_times, events, state_at


def replay(events):
    n = 0
    for t, mask in events:
        for f in mask:
            n = max(n, f + 1)
    running = [False] * n
    state_at = {}
    for t, mask in events:
        for f in mask:
            running[f] = not running[f]
        state_at[t] = tuple(running)
    return n, state_at


def holds_at(events, n, state_at, t):
    if t in state_at:
        return state_at[t]
    known = sorted(x for x in state_at if x < t)
    if not known:
        return (False,) * n
    return state_at[known[-1]]


def first_true(events, state_at, target):
    for t in sorted(state_at):
        if state_at[t][target]:
            return t
    return None


def last_true(events, state_at, target):
    last = None
    for t in sorted(state_at):
        if state_at[t][target]:
            last = t
    return last


def stream_prompt(events):
    parts = []
    for t, mask in events:
        parts.append(f"at {t}: toggle {','.join(f'F{f}' for f in mask)}")
    return "; ".join(parts)


def nfluents_of(events):
    n = 0
    for t, mask in events:
        for f in mask:
            n = max(n, f + 1)
    return n


class FluentPersistenceWindows(Task):
    summary = (
        "Rules initiate/terminate named fluents over an event history; replay with "
        "persistence across gaps: answer whether a fluent holds at time T, its first "
        "or last true instant, or every fluent holding at T."
    )
    design_choice = (
        "Answer format: a single canonical integer timestamp for first/last true instant, "
        "versus a canonical sorted list of fluent names for the set-at-T query."
    )
    config_cls = FluentPersistenceWindowsConfig
    task_version = 2

    def generate_entry(self):
        config = self.config
        n_fluents = config.n_fluents

        for _ in range(300):
            event_times, events, hist = build_history(config)
            n, state_at = replay(events)
            mode = random.choice(["holds", "first", "last", "set"])

            entry = self._build_entry(mode, events, n, state_at, config)
            if entry is not None:
                return entry

        raise RuntimeError("could not generate a valid instance")

    def _build_entry(self, mode, events, n, state_at, config):
        max_t = config.max_t
        nf = nfluents_of(events)
        if mode == "holds":
            t = random.randint(0, max_t)
            target = random.randrange(nf)
            vals = holds_at(events, n, state_at, t)
            answer = "yes" if vals[target] else "no"
            q = (
                f"Does F{target} hold at time {t}? "
                f"Answer exactly yes or no."
            )
            metadata = {
                "mode": "holds",
                "target": target,
                "time": t,
                "events": [(e[0], e[1]) for e in events],
                "max_t": max_t,
            }
        elif mode == "first":
            target = random.randrange(nf)
            f = first_true(events, state_at, target)
            answer = max_t + 1 if f is None else f
            q = (
                f"What is the first instant at which F{target} holds? "
                f"Answer a single integer timestamp, or {max_t + 1} if it never holds."
            )
            metadata = {
                "mode": "first",
                "target": target,
                "events": [(e[0], e[1]) for e in events],
                "max_t": max_t,
            }
        elif mode == "last":
            target = random.randrange(nf)
            f = last_true(events, state_at, target)
            answer = -1 if f is None else f
            q = (
                f"What is the last instant at which F{target} holds? "
                f"Answer a single integer timestamp, or -1 if it never holds."
            )
            metadata = {
                "mode": "last",
                "target": target,
                "events": [(e[0], e[1]) for e in events],
                "max_t": max_t,
            }
        else:
            t = random.randint(0, max_t)
            vals = holds_at(events, n, state_at, t)
            holding = sorted(f for f in range(nf) if vals[f])
            answer = "none" if not holding else ",".join(f"F{f}" for f in holding)
            q = (
                f"Which fluents hold at time {t}? "
                f"Answer a comma-separated sorted list of fluent names (e.g. F0,F2), "
                f"or the word none if no fluent holds."
            )
            metadata = {
                "mode": "set",
                "time": t,
                "events": [(e[0], e[1]) for e in events],
                "max_t": max_t,
            }

        if self._check_answer(answer, metadata):
            return Entry(metadata=metadata, answer=str(answer))
        return None

    def _check_answer(self, answer, metadata):
        score = _score(metadata, str(answer), metadata["mode"])
        return score == 1.0

    def render_prompt(self, metadata):
        fluents = "F0..F" + str(
            max((f for t, m in metadata["events"] for f in m), default=0))
        hist = stream_prompt(metadata["events"])
        q = self._question(metadata)
        return (
            f"Fluents: {fluents}. Initially none hold. Events toggle a fluent (on if "
            f"off, off if on): {hist}. "
            f"Fluents persist their truth between events. {q}"
        )

    def _question(self, metadata):
        m = metadata["mode"]
        if m == "holds":
            return (
                f"Does F{metadata['target']} hold at time {metadata['time']}? "
                f"Answer exactly yes or no."
            )
        if m == "first":
            return (
                f"What is the first instant at which F{metadata['target']} holds? "
                f"Answer a single integer timestamp, or {metadata['max_t'] + 1} if it "
                f"never holds."
            )
        if m == "last":
            return (
                f"What is the last instant at which F{metadata['target']} holds? "
                f"Answer a single integer timestamp, or -1 if it never holds."
            )
        return (
            f"Which fluents hold at time {metadata['time']}? "
            f"Answer a comma-separated sorted list of fluent names (e.g. F0,F2), "
            f"or the word none if no fluent holds."
        )

    def score_answer(self, answer, entry):
        metadata = entry["metadata"] if isinstance(entry, dict) else entry.metadata
        return _score(metadata, answer, metadata["mode"])


def _score(metadata, answer, mode):
    events = metadata["events"]
    n, state_at = replay(events)
    max_t = metadata.get("max_t")
    if mode == "holds":
        vals = holds_at(events, n, state_at, metadata["time"])
        expected = "yes" if vals[metadata["target"]] else "no"
        return 1.0 if answer == expected else 0.0
    if mode == "first":
        f = first_true(events, state_at, metadata["target"])
        expected = max_t + 1 if f is None else f
        return _num_match(answer, expected)
    if mode == "last":
        f = last_true(events, state_at, metadata["target"])
        expected = -1 if f is None else f
        return _num_match(answer, expected)
    vals = holds_at(events, n, state_at, metadata["time"])
    holding = sorted(f for f in range(n) if vals[f])
    expected = "none" if not holding else ",".join(f"F{f}" for f in holding)
    if not isinstance(answer, str):
        return 0.0
    if answer == expected:
        return 1.0
    return 0.0


def _num_match(answer, expected):
    if isinstance(answer, bool):
        return 0.0
    try:
        return 1.0 if int(answer) == expected else 0.0
    except (ValueError, TypeError):
        return 0.0


TASK_META = {
    'parent_source_id': None,
    'idea': 'fluent_persistence_windows (variant 1 of 3)',
    'hypothesis': 'P003',
    'changes': 'new task in '
               'reasoning_core/tasks/generated/k3_non_local_structured_r4/fluent_persistence_windows',
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
