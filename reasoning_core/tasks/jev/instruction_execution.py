"""Ground instructions in entity sets and apply guarded state changes.

Levels add groups, compound filters and exceptions, unavailable entities, transaction policies, deferred
operations, and ambiguous references. Ported from tasksource.jev.procedural.instruction_execution; its level tables
stop at 4.
"""
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision, pose
from reasoning_core.template import Config, Task

DOMAINS = [
    ("job", "running", "start", "stop"),
    ("document", "approved", "approve", "unapprove"),
    ("account", "enabled", "enable", "disable"),
    ("ticket", "escalated", "escalate", "de-escalate"),
    ("shipment", "held", "hold", "release"),
]
SITES = ["north", "south", "central", "west"]
TIERS = ["standard", "priority", "critical"]
COUNTS = [str(i) for i in range(9)] + ["9 or more"]  # Jev scores have at most 10 levels
RESOLUTIONS = ["execute", "partial", "blocked", "no_change", "clarify", "schedule", "rule", "query"]
DEFERRED = ["nothing", "one-time schedule", "recurring rule"]
N_ENTITIES = [3, 5, 8, 14, 22]
SEMANTICS = ("A request selects the named entities after any exclusions. Immediate updates set the named boolean "
             "property to the requested value. Unavailable entities cannot be changed. Atomic requests change "
             "nothing if any selected entity is unavailable; best-effort requests skip unavailable entities. "
             "Ordered requests perform steps in order, including repeated updates, and skip unavailable entities "
             "like best-effort requests. Clarify an ambiguous or "
             "missing name without changing anything. A query only reads state. A schedule or recurring rule "
             "is registered now and does not immediately modify entity properties.")


def _execute(state, spec):
    entities = {e["id"]: dict(e) for e in state["entities"]}
    ids, kind, prop = spec["ids"], spec["kind"], state["property"]
    if kind == "clarify":
        status = "clarify"
    elif kind in ("query", "schedule", "rule"):
        status = kind
    elif not ids:
        status = "no_change"
    else:
        unavailable = [i for i in ids if not entities[i]["available"]]
        available = [i for i in ids if entities[i]["available"]]
        if unavailable and state["execution_policy"] == "atomic" or not available:
            status = "blocked"
        else:
            status = "partial" if unavailable else "execute"
            for value in spec["values"]:
                for i in available:
                    entities[i][prop] = value
            original = {e["id"]: e[prop] for e in state["entities"]}
            if status == "execute" and len(spec["values"]) == 1 and all(
                    entities[i][prop] == original[i] for i in ids):
                status = "no_change"
    changed = sum(e[prop] != entities[e["id"]][prop] for e in state["entities"])
    return status, entities, changed


@dataclass
class InstructionExecutionConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class InstructionExecution(Task):
    summary = ("Ground a request over entities (by name, group, site/tier filter, exclusions, ambiguous names) and "
               "apply it under atomic/best-effort/ordered policies, queries, schedules and rules; ask resolution, "
               "targets, final state and net changes.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or InstructionExecutionConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        noun, prop, positive, negative = rng.choice(DOMAINS)
        n = N_ENTITIES[level] + rng.randint(0, max(1, level))
        entities = [
            {"id": f"E{i+1}", "name": f"{noun} {i+1}", "site": rng.choice(SITES),
             "tier": rng.choice(TIERS), "available": True, prop: bool(rng.getrandbits(1))}
            for i in range(n)
        ]
        by_id = {e["id"]: e for e in entities}
        groups = {"batch A": [e["id"] for e in entities if int(e["id"][1:]) % 2],
                  "batch B": [e["id"] for e in entities if not int(e["id"][1:]) % 2]}
        wanted = bool(rng.getrandbits(1))
        verb = positive if wanted else negative
        selector_kind = rng.choice(["id", "group"] if level == 1 else
                                   ["id", "group", "filter"] if level >= 2 else ["id"])
        if selector_kind == "id":
            chosen = rng.choice(entities)
            ids = [chosen["id"]]
            selector = chosen["name"]
        elif selector_kind == "group":
            group = rng.choice(list(groups))
            ids = list(groups[group])
            selector = f"all {noun}s in {group}"
        else:
            exemplar = rng.choice(entities)
            site = exemplar["site"]
            tier = exemplar["tier"] if level >= 3 else None
            ids = [e["id"] for e in entities if e["site"] == site and (tier is None or e["tier"] == tier)]
            selector = f"all {noun}s at site {site}" + (f" with tier {tier}" if tier else "")
        if level >= 2 and len(ids) > 1 and rng.random() < 0.5:
            exclude = rng.choice(ids)
            ids.remove(exclude)
            selector += f", except {by_id[exclude]['name']}"
        kind = "immediate"
        if level >= 2:
            kind = rng.choices(["immediate", "query", "schedule", "rule"], [6, 1, 1, 1])[0]
        if level >= 3 and rng.random() < 0.12:
            kind = "clarify"
            if rng.random() < 0.75:
                a, b = rng.sample(entities, 2)
                b["name"] = a["name"]
                selector = a["name"]
            else:
                selector = f"{noun} not listed"
            ids = []
        if level >= 2 and kind == "immediate":
            for i in ids:
                if rng.random() < (0.15 if level == 2 else 0.35):
                    by_id[i]["available"] = False
        policy = "atomic" if level < 3 else rng.choice(["atomic", "best_effort", "ordered"])
        values = [wanted]
        if level >= 4 and kind == "immediate" and rng.random() < 0.4:
            policy = "ordered"
            values = [not wanted, wanted]
        if kind == "query":
            request = f"Are {selector} currently {prop}?"
        elif kind == "schedule":
            request = f"At 18:30, {verb} {selector}."
        elif kind == "rule":
            request = f"Whenever a review event occurs, {verb} {selector}."
        elif len(values) > 1:
            request = f"First {negative if wanted else positive} {selector}, then {verb} them."
        else:  # immediate or clarify
            request = f"Please {verb} {selector}."
        state = {"entity_type": noun, "property": prop, "entities": entities, "groups": groups,
                 "execution_policy": policy, "semantics": SEMANTICS, "request": request}
        status, final, changed = _execute(state, {"kind": kind, "ids": ids, "values": values})
        probe = rng.choice(entities)
        if ids and rng.random() < 0.6:
            probe = by_id[rng.choice(ids)]
        pid = probe["id"]
        questions = {
            "resolution": Decision(status, criteria=dict.fromkeys(RESOLUTIONS), instructions=
                                   "How should the request be handled under the stated execution policy?"),
            "target_count": Decision(min(len(ids), 9), type="score", criteria=COUNTS, instructions=
                "How many entities are unambiguously selected by the request, before checking availability?"),
            "probe_selected": Decision(pid in ids, type="noul", instructions=
                                       f"Is {pid} in the unambiguous target set?"),
            "probe_final_state": Decision(final[pid][prop], type="noul", instructions=
                                          f"Immediately after handling the request, is {pid}.{prop} true?"),
            "changed_count": Decision(min(changed, 9), type="score", criteria=COUNTS, instructions=
                                      "How many entity properties change immediately (net changes)?"),
            "deferred_registration": Decision(
                {"schedule": DEFERRED[1], "rule": DEFERRED[2]}.get(status, DEFERRED[0]),
                criteria=dict.fromkeys(DEFERRED), instructions="What is registered for later, if anything?"),
        }
        return pose(questions, state, state_seed, question)
