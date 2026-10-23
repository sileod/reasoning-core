"""Tag every mention of the events that stand in a stated relation to a given event: its causes or effects, direct or
through other events, in a narrative; or what follows from facts and if-then rules, what triggers an event and what
an event triggers, in a rule set.

Latent structure: events of one theme. A narrative is a time-ordered DAG of causal edges, plus ordered pairs that
are only temporal ("A happened before B") or explicitly not causal ("A preceded B but did not cause it"), never
between events joined by a causal path. A rule set is if-then rules, some conjunctive, with facts that events
occurred or did not; forward chaining gives what follows, and no stated non-occurrence is derivable. Answers are
every mention of each related event, null when there is none; a null cause has a temporal or ruled-out look-alike,
a null consequence has a rule whose condition does not hold. The renderer words each edge, rule and fact several
ways and shuffles their order. Levels add events, edges, temporal and ruled-out look-alikes, shuffling, transitive
questions, conjunctive rules and missing relations.
"""
import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import Doc, extraction_entry

THEMES = {
    "plant": ["coolant leak", "pump failure", "press overheating", "line shutdown", "sensor fault", "power surge",
              "generator start", "fire alarm", "evacuation", "safety inspection", "shipment delay", "product recall",
              "overtime shift", "valve repair"],
    "software": ["database outage", "cache flush", "traffic spike", "login failure", "deploy rollback",
                 "disk saturation", "certificate expiry", "pager alert", "region failover", "incident review",
                 "queue backlog", "memory leak", "config change", "API timeout"],
    "region": ["heavy rainfall", "river flooding", "road closure", "crop loss", "price increase", "landslide",
               "power cut", "school closure", "drought", "wildfire", "water rationing", "bridge collapse",
               "tourist decline", "aid appeal"],
    "hospital": ["staff shortage", "bed shortage", "flu outbreak", "ward closure", "surgery backlog",
                 "ambulance diversion", "supply delay", "budget cut", "overtime ban", "patient transfer",
                 "audit visit", "system upgrade", "pharmacy error", "waiting list growth"],
}
CAUSAL = ["{A} caused {b}.", "{B} was caused by {a}.", "{A} led directly to {b}.",
          "Because of {a}, {b} followed.", "{B} was a direct result of {a}."]
TEMPORAL = ["{A} happened before {b}.", "{B} came after {a}.",
            "Shortly after {a}, {b} was reported.", "{A} took place earlier than {b}."]
RULED_OUT = ["{A} preceded {b} but did not cause it.",
             "{B} followed {a}, though {a} was not its cause.",
             "Investigators ruled out {a} as a cause of {b}."]
RULES = ["If {a} occurs, {b} follows.", "{B} is triggered whenever {a} occurs.",
         "{A} always leads to {b}."]
RULES2 = ["If both {a} and {c} occur, {b} follows.", "{A} together with {c} triggers {b}."]
FACTS = ["{A} occurred.", "{A} has been confirmed."]
NOT_FACTS = ["{A} did not occur.", "{A} was avoided."]


@dataclass
class RelationalSpanExtractionConfig(Config):
    events: float = 4.0
    causal: float = 0.8
    temporal: float = 0.5
    ruled_out: float = 0.0
    shuffle: float = 0.0
    transitive: float = 0.0
    conjunctive: float = 0.0
    missing: float = 0.15
    fields: float = 2.0

    def apply_difficulty(self, level):
        self.events = 4 + 1.5 * level
        self.causal = 0.8 + 0.1 * level
        self.temporal = 0.5 + 0.25 * level
        self.ruled_out = 0.1 * level
        self.shuffle = min(1.0, 0.25 * level)
        self.transitive = min(0.5, 0.12 * level)
        self.conjunctive = 0.1 * level
        self.missing = 0.15 + 0.0625 * level
        self.fields = 2 + 0.75 * level


class RelationalSpanExtraction(Task):
    summary = ("Every mention of the events related to a given one: its direct or indirect causes or effects in a "
               "narrative where some ordered events are only temporal or explicitly not causal, or what follows from "
               "facts and if-then rules, what triggers an event and what it triggers; null when the relation is not "
               "stated although a temporal or rule look-alike is.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or RelationalSpanExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng = random.Random(state_seed)
        theme = rng.choice(sorted(THEMES))
        n = min(len(THEMES[theme]), max(3, sround(self.config.events, seed=rng.random())))
        events = rng.sample(THEMES[theme], n)  # in time order for a narrative
        if rng.random() < 0.5:
            sentences, fields = self._narrative(rng, events)
            kind = "narrative"
        else:
            sentences, fields = self._rules(rng, events)
            kind = "rules"
        if rng.random() < self.config.shuffle:
            rng.shuffle(sentences)
        doc = Doc()
        for template, slots in sentences:  # an uppercase slot starts the sentence
            names = {k: re.search(r"\{(%s)\}" % k, template, re.I)[1] for k in slots}
            doc.add(template + " ", **{names[k]: (("The " if names[k].isupper() else "the ") + e, e)
                                       for k, e in slots.items()})
        spans = {f["name"]: [s for e in f.pop("events") for s in doc.marks.get(e, [])] for f in fields}
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, kind=kind, theme=theme)

    def _narrative(self, rng, events):
        c, n = self.config, len(events)
        causes = {e: set() for e in events}
        for j in range(1, n):  # each event draws its direct causes among earlier ones
            for i in range(j):
                if rng.random() < c.causal / j:
                    causes[events[j]].add(events[i])

        def ancestors(e):
            out, todo = set(), list(causes[e])
            while todo:
                a = todo.pop()
                if a not in out:
                    out.add(a)
                    todo += causes[a]
            return out

        up = {e: ancestors(e) for e in events}
        down = {e: {d for d in events if e in up[d]} for e in events}
        unrelated = [(events[i], events[j]) for i in range(n) for j in range(i + 1, n)
                     if events[i] not in up[events[j]]]
        rng.shuffle(unrelated)
        k_temporal = min(len(unrelated), sround(c.temporal * n / 2, seed=rng.random()))
        k_ruled = min(len(unrelated) - k_temporal, sround(c.ruled_out * n / 2, seed=rng.random()))
        sentences = [(rng.choice(CAUSAL), {"a": a, "b": b})
                     for b in events for a in sorted(causes[b], key=events.index)]
        sentences += [(rng.choice(TEMPORAL), {"a": a, "b": b}) for a, b in unrelated[:k_temporal]]
        sentences += [(rng.choice(RULED_OUT), {"a": a, "b": b}) for a, b in unrelated[k_temporal:k_temporal + k_ruled]]
        sentences.sort(key=lambda s: (events.index(s[1]["b"]), events.index(s[1]["a"])))
        mentioned = {e for _, s in sentences for e in s.values()}

        fields, asked = [], set()
        for k in range(max(1, sround(c.fields, seed=rng.random()))):
            direction = rng.choice(["causes", "effects"])
            transitive = rng.random() < c.transitive
            relation = (up if transitive else causes) if direction == "causes" else \
                (down if transitive else {e: {d for d in events if e in causes[d]} for e in events})
            empty = [e for e in mentioned if not relation[e]]
            full = [e for e in mentioned if relation[e]]
            pool = empty if empty and (rng.random() < c.missing or not full) else full
            x = rng.choice(sorted(pool))
            if (x, direction, transitive) in asked:
                continue
            asked.add((x, direction, transitive))
            if direction == "causes":
                instruction = (f"Every event that led to the {x}, directly or through other events." if transitive
                               else rng.choice([f"Every direct cause of the {x}.",
                                                f"Every event that directly caused the {x}."]))
            else:
                instruction = (f"Every event the {x} led to, directly or through other events." if transitive
                               else rng.choice([f"Every direct effect of the {x}.",
                                                f"Every event the {x} directly caused."]))
            fields.append({"name": f"{'all_' if transitive else ''}{direction}_{k + 1}", "type": "list",
                           "instruction": instruction, "events": sorted(relation[x])})
        return sentences, fields

    def _rules(self, rng, events):
        c = self.config
        rules = []  # (antecedents, consequent)
        for j, b in enumerate(events[1:], 1):
            if rng.random() < 0.8:
                if j >= 2 and rng.random() < c.conjunctive:
                    rules.append((tuple(rng.sample(events[:j], 2)), b))
                else:
                    rules.append(((rng.choice(events[:j]),), b))
        sources = [e for e in events if not any(r[1] == e for r in rules)]
        facts = {e for e in sources if rng.random() < 0.6} or {rng.choice(sources)}

        derived, changed = set(facts), True
        while changed:
            changed = False
            for ante, b in rules:
                if b not in derived and all(a in derived for a in ante):
                    derived.add(b)
                    changed = True
        not_facts = [e for e in sources if e not in facts and rng.random() < 0.7]
        sentences = [(rng.choice(RULES2 if len(ante) == 2 else RULES),
                      {"a": ante[0], "b": b, **({"c": ante[1]} if len(ante) == 2 else {})}) for ante, b in rules]
        sentences += [(rng.choice(FACTS), {"a": e}) for e in sorted(facts, key=events.index)]
        sentences += [(rng.choice(NOT_FACTS), {"a": e}) for e in not_facts]
        mentioned = {e for _, s in sentences for e in s.values()}

        triggers = {e: {a for ante, b in rules if b == e for a in ante} for e in events}
        triggered = {e: {b for ante, b in rules if e in ante} for e in events}
        fields, asked = [], set()
        for k in range(max(1, sround(c.fields, seed=rng.random()))):
            q = rng.choice(["follows", "triggers", "triggered"])
            if q == "follows":
                if "follows" in asked:
                    continue
                asked.add("follows")
                fields.append({"name": f"follows_{k + 1}", "type": "list", "events": sorted(derived - facts),
                               "instruction": "Every event that the rules imply must also occur, starting from the "
                                              "events stated to have occurred (not counting those)."})
                continue
            relation = triggers if q == "triggers" else triggered
            empty = [e for e in mentioned if not relation[e]]
            full = [e for e in mentioned if relation[e]]
            pool = empty if empty and (rng.random() < c.missing or not full) else full
            x = rng.choice(sorted(pool))
            if (x, q) in asked:
                continue
            asked.add((x, q))
            instruction = (f"Every event that a rule names as a condition for the {x}." if q == "triggers" else
                           f"Every event that a rule says follows from the {x}, alone or together with another event.")
            fields.append({"name": f"{'conditions' if q == 'triggers' else 'consequences'}_{k + 1}", "type": "list",
                           "instruction": instruction, "events": sorted(relation[x])})
        return sentences, fields
