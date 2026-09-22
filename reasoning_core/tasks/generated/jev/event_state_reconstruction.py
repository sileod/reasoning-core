import json
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Entry, Task, edict, stochastic_rounding as sround
from reasoning_core.tasks.generated.jev._common import canonical_json, choice_answer, jev_prompt, json_score, noul_answer, score_answer


OWNERS = ["alice", "bob", "carol", "unassigned"]
SEVERITY = ["Routine.", "Degraded service requiring attention.", "Critical user-blocking incident."]


@dataclass
class JevEventStateReconstructionConfig(Config):
    n_events: int = 6

    def apply_difficulty(self, level):
        self.n_events = sround(self.n_events + 1.5 * level)


class JevEventStateReconstruction(Task):
    summary = "Reconstruct current owner, open status, and severity from shuffled timestamped events plus a stale snapshot using parallel Jev questions."
    config_cls = JevEventStateReconstructionConfig

    def generate_entry(self):
        owner = random.choice(OWNERS[:-1])
        is_open = True
        severity = random.randrange(3)
        initial = {"owner": owner, "open": is_open, "severity": severity}
        history = [dict(initial)]
        events = []
        ts = 100
        for i in range(max(3, self.config.n_events)):
            ts += random.randint(1, 8)
            kind = random.choice(["assign", "severity", "resolve", "reopen", "note"])
            event = {"ts": ts, "kind": kind}
            if kind == "assign":
                owner = random.choice(OWNERS)
                event["owner"] = owner
            elif kind == "severity":
                severity = random.randrange(3)
                event["severity"] = severity
            elif kind == "resolve":
                is_open = False
            elif kind == "reopen":
                is_open = True
            else:
                event["text"] = random.choice(["ack", "triage", "customer update"])
            events.append(event)
            history.append({"owner": owner, "open": is_open, "severity": severity})
        snapshot_cut = random.randrange(len(events))
        snapshot = history[snapshot_cut + 1]
        presented = list(events)
        random.shuffle(presented)
        state = {
            "initial_state": initial,
            "stale_snapshot": {"as_of": events[snapshot_cut]["ts"], **snapshot},
            "events": presented,
            "rule": "Start from initial_state and apply events in ascending timestamp order. stale_snapshot is an older redundant view and must not override later events.",
        }
        questions = {
            "current_owner": {"type": "choice", "instructions": "Who owns the incident after replaying the event log?", "criteria": {x: x for x in OWNERS}},
            "is_open": {"type": "noul", "instructions": "Is the incident open after replaying the event log?"},
            "current_severity": {"type": "score", "instructions": "What is the incident's current severity after replaying the event log?", "criteria": SEVERITY},
        }
        answers = {
            "current_owner": choice_answer(owner, OWNERS),
            "is_open": noul_answer(is_open),
            "current_severity": score_answer(severity, SEVERITY),
        }
        return Entry(metadata=edict(state=state, questions=questions), answer=canonical_json(answers))

    def render_prompt(self, m):
        return jev_prompt(m.state, m.questions)

    def score_answer(self, answer, entry):
        return json_score(answer, entry)

    def balancing_key(self, problem):
        a = json.loads(problem.answer)
        return a["current_owner"]["choice"], int(a["is_open"]["noul"])
