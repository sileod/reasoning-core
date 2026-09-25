import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task


PRIMITIVES = [
    ("open", "open"),
    ("close", "closed"),
    ("fill", "full"),
    ("empty", "empty"),
    ("lock", "locked"),
    ("unlock", "unlocked"),
    ("start", "running"),
    ("stop", "stopped"),
]


SUBJECTS = ["Ada", "Ben", "Cara", "Dan", "Eve", "Finn", "Gus", "Ida", "Jon", "Kay"]
OBJECTS = ["window", "door", "box", "tank", "gate", "well", "shutter", "safe", "gate", "locker"]


def _find_repetitive_witness(events, f):
    ev = events[f]
    for j in range(f - 1, -1, -1):
        if events[j]["subject"] == ev["subject"] and events[j]["action"] == ev["action"]:
            return j
    return None


def _find_restitutive_witness(events, f):
    ev = events[f]
    for j in range(f - 1, -1, -1):
        if events[j]["object"] == ev["object"]:
            if events[j]["state"] == ev["state"]:
                return j
            return None
    return None


def _answer_tokens(readings):
    return ["None" if r["witness"] is None else f"E{r['witness']}" for r in readings]


@dataclass
class WitnessConfig(Config):
    n_events: int = 5
    n_focus: int = 2
    n_subjects: int = 5
    n_objects: int = 4

    def apply_difficulty(self, level):
        self.n_events = 5 + level
        self.n_focus = max(1, 2 + level // 2)
        self.n_subjects = 5 + level
        self.n_objects = 4 + (level + 1) // 2


class RepetitionRestitutionWitnesses(Task):
    summary = ("Match repetitive and restitutive readings to prior events or result "
               "states across participant changes, interrupted states, and nested "
               "event decompositions; answer which readings have an appropriate earlier witness.")
    design_choice = ("Answer as a canonical list of event IDs that witness each "
                     "repetitive/restitutive reading, with IDs drawn from a fixed "
                     "pool and ordered by reading index.")
    config_cls = WitnessConfig

    def generate_entry(self):
        cfg = self.config
        n_events = max(2, cfg.n_events)
        n_subject = max(2, cfg.n_subjects)
        n_object = max(2, cfg.n_objects)
        n_focus = max(1, min(cfg.n_focus, n_events - 1))

        subjects = SUBJECTS[:n_subject]
        objects = OBJECTS[:n_object]

        for _ in range(300):
            events = []
            for i in range(n_events):
                action, state = random.choice(PRIMITIVES)
                events.append(
                    {
                        "idx": i,
                        "subject": random.choice(subjects),
                        "action": action,
                        "object": random.choice(objects),
                        "state": state,
                    }
                )

            focus = list(range(n_events - n_focus, n_events))
            readings = []
            for f in focus:
                readings.append(
                    {"type": "repetitive", "focus": f, "witness": _find_repetitive_witness(events, f)}
                )
                readings.append(
                    {"type": "restitutive", "focus": f, "witness": _find_restitutive_witness(events, f)}
                )

            tokens = _answer_tokens(readings)
            if len(set(tokens)) >= 2:
                rep_seen = any(r["type"] == "repetitive" and r["witness"] is not None for r in readings)
                res_seen = any(r["type"] == "restitutive" and r["witness"] is not None for r in readings)
                rep_none = any(r["type"] == "repetitive" and r["witness"] is None for r in readings)
                res_none = any(r["type"] == "restitutive" and r["witness"] is None for r in readings)
                if rep_seen and res_none and rep_none and res_seen:
                    break
        else:
            raise RuntimeError("repetition_restitution_witnesses: could not find a varied scenario")

        for r in readings:
            if r["type"] == "repetitive":
                assert _find_repetitive_witness(events, r["focus"]) == r["witness"]
            else:
                assert _find_restitutive_witness(events, r["focus"]) == r["witness"]

        answer = " ".join(_answer_tokens(readings))
        return Entry(
            metadata={
                "events": events,
                "readings": readings,
                "n_subjects": n_subject,
                "n_objects": n_object,
            },
            answer=answer,
        )

    def render_prompt(self, metadata):
        events = metadata["events"]
        readings = metadata["readings"]
        lines = ["A chronologically ordered sequence of events E0, E1, ... occurs. "
                 "Each event lists who performed what action on which object and the "
                 "resulting state of that object."]
        for ev in events:
            lines.append(
                f"E{ev['idx']}: {ev['subject']} {ev['action']} the {ev['object']}; "
                f"afterwards the {ev['object']} is {ev['state']}."
            )
        lines.append("")
        lines.append(
            "A repetitive reading needs an earlier event by the SAME subject performing the SAME "
            "action; its witness is the most recent such earlier event. A restitutive reading needs "
            "the object to already be in that state: it is witnessed by the most recent earlier "
            "event that touched the SAME object and left it in that SAME state (an intermediate "
            "change would have interrupted it). Use 'None' when no earlier event witnesses the reading."
        )
        lines.append("")
        for i, r in enumerate(readings):
            ev = events[r["focus"]]
            if r["type"] == "repetitive":
                lines.append(f"R{i}: Repetitive reading of E{ev['idx']}: {ev['subject']} "
                             f"{ev['action']} the {ev['object']} again.")
            else:
                lines.append(f"R{i}: Restitutive reading of E{ev['idx']}: the {ev['object']} "
                             f"is {ev['state']} again.")
        lines.append("")
        lines.append(
            "Give each reading's most recent appropriate earlier-witness event, in reading order "
            "R0, R1, ..., as a space-separated list of event IDs (like E2) or the word None for "
            "an unwitnessed reading."
        )
        return "\n".join(lines)

    def score_answer(self, answer, entry):
        reference = entry["answer"]
        if not isinstance(answer, str):
            return 0.0
        a = " ".join(answer.strip().split())
        r = " ".join(reference.strip().split())
        return 1.0 if a and a == r else 0.0


TASK_META = {'parent_source_id': None,
 'idea': 'repetition_restitution_witnesses (variant 1 of 3)',
 'hypothesis': 'P002',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/ua_scope_and_binding_r4/repetition_restitution_witnesses',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': '1.18.32',
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 1475571465,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 56,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}
