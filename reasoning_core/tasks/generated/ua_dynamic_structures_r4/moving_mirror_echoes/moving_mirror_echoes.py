import math
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, stochastic_rounding


@dataclass
class MovingMirrorEchoesConfig(Config):
    n_segments: int = 3
    max_events: int = 1
    speed: int = 100

    def apply_difficulty(self, level):
        self.n_segments = stochastic_rounding(3 + 1 * level)
        self.max_events = stochastic_rounding(1 + 1 * level)
        self.speed = 100 + 20 * level


def _simulate(speed, segments, events):
    n = len(segments)

    active = [False] * n
    plist = [0.0] * n
    vlist = [0.0] * n

    cur_time = 0.0
    evi = 0
    while evi < len(events):
        kind, idx, t = events[evi]
        if t < cur_time:
            raise ValueError("bad event order")
        dt = t - cur_time
        if dt > 0:
            for k in range(n):
                if active[k]:
                    plist[k] += vlist[k] * dt
        if kind == 1:
            active[idx] = True
            a, _, v = segments[idx]
            plist[idx] = a + v * t
            vlist[idx] = v
        else:
            active[idx] = False
        cur_time = t
        evi += 1

    pulse_pos = 0.0
    pulse_vel = speed
    freq = speed
    max_steps = 4000
    step = 0
    arrival_t = None

    while step < max_steps:
        step += 1
        if not any(active):
            raise ValueError("no active mirrors")
        best = None
        for k in range(n):
            if not active[k]:
                continue
            rel = pulse_vel - vlist[k]
            if abs(rel) < 1e-9:
                continue
            tau = (plist[k] - pulse_pos) / rel
            if tau > 1e-9 and (best is None or tau < best[0]):
                best = (tau, k)
        if best is None:
            raise ValueError("never hit a mirror")
        tau, k = best
        pulse_pos += pulse_vel * tau
        for j in range(n):
            if active[j]:
                plist[j] += vlist[j] * tau
        cur_time += tau

        if not active[k]:
            raise ValueError("dephased")
        vmir = vlist[k]
        rel_before = pulse_vel - vmir
        new_vel = -rel_before + vmir
        if abs(new_vel) < 1e-9:
            raise ValueError("degenerate reflection")
        freq = freq * (new_vel / pulse_vel)
        pulse_vel = new_vel

        if pulse_pos <= 0.0 and step >= 2:
            arrival_t = cur_time
            break

    if arrival_t is None or arrival_t <= 0:
        raise ValueError("no arrival")
    return arrival_t, freq


class MovingMirrorEchoes(Task):
    summary = "Propagate light pulses among piecewise uniformly moving mirrors with activation and removal events; resolve successive interceptions and Doppler shifts, returning an arrival time or received frequency."
    design_choice = "Mirrors are arranged on a 1D line; each pulse has a fixed speed and the answer is the time of the first interception after all events, given as an integer in microseconds."
    config_cls = MovingMirrorEchoesConfig

    def generate_entry(self):
        cfg = self.config
        speed = cfg.speed
        while True:
            entry = self._attempt(cfg, speed)
            if entry is not None:
                return entry

    def _attempt(self, cfg, speed):
        sim_time = random.uniform(4.0, 50.0)

        segments = []
        pos = random.uniform(5.0, 15.0)
        for _ in range(cfg.n_segments):
            seg_len = random.uniform(15.0, 40.0)
            vel = random.choice([-1.0, 1.0]) * random.uniform(0.5, 3.0)
            end_pos = pos + seg_len
            segments.append((pos, end_pos, vel))
            pos = end_pos

        n = len(segments)

        events = []
        for idx in range(n):
            events.append([1, idx, 0.0])
        active_flags = [True] * n
        attempts = 0
        want_events = n + cfg.max_events
        while len(events) < want_events and attempts < 200:
            attempts += 1
            idx = random.randrange(n)
            t = round(random.uniform(0.5, sim_time), 4)
            if active_flags[idx]:
                events.append([0, idx, t])
                active_flags[idx] = False
            else:
                events.append([1, idx, t])
                active_flags[idx] = True
        events.sort(key=lambda e: (e[2], e[1]))

        cleaned = []
        flags = [True] * n
        for kind, idx, t in events:
            if t == 0.0:
                cleaned.append([kind, idx, t])
                continue
            if kind == 1:
                if not flags[idx]:
                    cleaned.append([kind, idx, t])
                    flags[idx] = True
            else:
                if flags[idx]:
                    cleaned.append([kind, idx, t])
                    flags[idx] = False
        events = cleaned

        if not any(flags):
            return None

        try:
            arrival_time, received_freq = _simulate(speed, segments, events)
        except ValueError:
            return None

        if not (arrival_time > 0):
            return None
        if not (received_freq > 0):
            return None

        answer_is_time = random.random() < 0.6
        if answer_is_time:
            ans_us = int(arrival_time * 1000.0 + 0.5)
            answer = str(ans_us)
        else:
            answer = str(int(received_freq + 0.5))

        events_repr = [
            {
                "kind": "activate" if ev[0] == 1 else "remove",
                "index": ev[1],
                "time": ev[2],
            }
            for ev in events
        ]

        mirrors_repr = [
            {
                "index": i,
                "x0": round(seg[0], 4),
                "v": round(seg[2], 4),
            }
            for i, seg in enumerate(segments)
        ]

        return Entry(
            metadata={
                "speed": speed,
                "events": events_repr,
                "mirrors": mirrors_repr,
                "answer_is_time": answer_is_time,
                "arrival_time_s": round(arrival_time, 6),
                "received_freq": round(received_freq, 4),
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        speed = metadata["speed"]
        events = metadata["events"]
        lines = []
        for ev in events:
            lines.append(
                f"- {ev['kind']} mirror {ev['index'] + 1} at t={ev['time']} us"
            )
        event_text = "\n".join(lines)
        mirror_text = ", ".join(
            f"mirror {m['index'] + 1} at x={m['x0']} moving at v={m['v']} u/us"
            for m in metadata["mirrors"]
        )
        if metadata["answer_is_time"]:
            return (
                f"A light pulse departs the origin at t=0 heading right with "
                f"speed {speed} units/us. Mirrors sit on the positive 1D line "
                f"and move piecewise uniformly; each reflection reverses the "
                f"pulse's velocity relative to the mirror and scales its "
                f"frequency by the Doppler factor. Initial state: {mirror_text}."
                f" Events:\n{event_text}\n"
                f"After all events, compute the time in microseconds at which "
                f"the pulse first returns to the origin. Answer as an integer."
            )
        else:
            return (
                f"A light pulse departs the origin at t=0 heading right with "
                f"speed {speed} units/us. Mirrors sit on the positive 1D line "
                f"and move piecewise uniformly; each reflection reverses the "
                f"pulse's velocity relative to the mirror and scales its "
                f"frequency by the Doppler factor. Initial state: {mirror_text}."
                f" Events:\n{event_text}\n"
                f"After all events, compute the received frequency of the "
                f"pulse after its first interception by an activated mirror. "
                f"Answer as an integer."
            )

    def score_answer(self, answer, entry):
        target = entry["answer"]
        return 1.0 if answer == target else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'moving_mirror_echoes (variant 1 of 3)',
 'hypothesis': 'P006',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_dynamic_structures_r4/moving_mirror_echoes',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 798610012,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
