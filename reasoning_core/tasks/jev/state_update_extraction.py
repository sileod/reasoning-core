"""Read the current (or previous) value of each slot of a plan from a chat log of changes.

Values are set, proposed and then approved, rejected or left pending, corrected, and undone; only effective changes
count, so the answer is the span that set the value now in force (an approved proposal's span, the earlier span an
undo restores) and a slot that was only ever proposed is null. From level 2 the messages may be out of order and
must be sorted by their times. Levels add plans, slots, messages and ineffective changes.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import FIRST, LAST, MONTHS, Doc, extraction_entry

PLANS = ["kickoff meeting", "budget review", "client dinner", "team offsite", "training session", "product demo",
         "board call", "site visit"]
# slot -> (value(rng), set, propose, correct); {o} is the plan, {v} the value, {p} a person, {x} the replaced value
SLOTS = {
    "date": (lambda rng: f"{rng.randint(1, 28)} {rng.choice(MONTHS)}",
             ["The {o} is scheduled for {v}.", "The {o} will be on {v}.", "Moving the {o} to {v}."],
             ["Could we move the {o} to {v}?", "I suggest holding the {o} on {v} instead."],
             "Correction: the {o} is on {v}, not {x}."),
    "venue": (lambda rng: f"Room {rng.randint(1, 6)}{rng.choice('ABCD')}",
              ["The {o} will take place in {v}.", "Booked {v} for the {o}.", "The {o} is now in {v}."],
              ["What about {v} for the {o}?", "I suggest we book {v} for the {o}."],
              "Correction: the {o} is in {v}, not {x}."),
    "host": (lambda rng: f"{rng.choice(FIRST)} {rng.choice(LAST)}",
             ["{v} will host the {o}.", "The {o} is hosted by {v}.", "{v} takes over hosting the {o}."],
             ["Maybe {v} could host the {o}?", "I suggest {v} as host of the {o}."],
             "Correction: {v} hosts the {o}, not {x}."),
    "budget": (lambda rng: f"€{rng.randint(4, 90) * 50:,}",
               ["The budget for the {o} is {v}.", "The {o} budget is set to {v}."],
               ["Could we raise the {o} budget to {v}?", "I suggest a budget of {v} for the {o}."],
               "Correction: the {o} budget is {v}, not {x}."),
}
APPROVE = ["Approved: the {s} change proposed for the {o}.", "OK, go ahead with that {s} for the {o}."]
REJECT = ["No, the {o} keeps its {s}.", "Rejected: the {s} change proposed for the {o}."]
UNDO = ["Undo the last {s} change for the {o}; it goes back to what it was.",
        "Cancel the latest change of {s} for the {o} and restore the previous one."]


@dataclass
class StateUpdateExtractionConfig(Config):
    plans: float = 1.0
    slots: float = 2.0
    messages: float = 3.0
    ineffective: float = 0.2
    unordered: float = 0.0
    previous: float = 0.0

    def apply_difficulty(self, level):
        self.plans = 1 + 0.5 * level
        self.slots = 2 + level
        self.messages = 3 + 3 * level
        self.ineffective = min(0.6, 0.2 + 0.1 * level)
        self.unordered = min(0.8, max(0.0, 0.3 * (level - 1)))
        self.previous = min(0.5, 0.15 * level)


class StateUpdateExtraction(Task):
    summary = ("Extract the value in force (or the one before the last change) of plan slots from a timestamped "
               "chat of sets, proposals approved/rejected/pending, corrections and undos, possibly out of order.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or StateUpdateExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        plans = rng.sample(PLANS, min(len(PLANS), max(1, sround(c.plans, seed=rng.random()))))
        pairs = rng.sample([(o, s) for o in plans for s in sorted(SLOTS)],
                           min(len(plans) * len(SLOTS), max(2, sround(c.slots, seed=rng.random()))))
        people = [f"{f} {l}" for f, l in zip(rng.sample(FIRST, 4), rng.sample(LAST, 4))]
        timeline = {pair: [] for pair in pairs}  # effective (value, mark) in time order
        pending, simple, undone = {}, dict.fromkeys(pairs, True), set()
        messages, marks = [], 0  # (text template, slots)

        touched = set()

        def say(message):  # a message about the current pair
            messages.append(message)
            touched.add(pair)

        def mention(value):
            nonlocal marks
            marks += 1
            return value, f"m{marks}"

        for _ in range(max(2, sround(c.messages, seed=rng.random()))):
            o, s = pair = rng.choice(pairs)
            value_of, sets, proposals, correction = SLOTS[s]
            line = timeline[pair]
            current = line[-1][0] if line else None
            if pair in pending:
                proposed = pending.pop(pair)
                if rng.random() < c.ineffective:
                    say((rng.choice(REJECT), {"o": o, "s": s}))
                elif rng.random() < 0.8:
                    say((rng.choice(APPROVE), {"o": o, "s": s}))
                    line.append(proposed)
                    undone.discard(pair)
                continue  # otherwise the proposal stays pending, then is forgotten
            value = value_of(rng)
            if value == current:
                continue
            roll = rng.random()
            if roll < c.ineffective:
                pending[pair] = v = mention(value)
                say((rng.choice(proposals), {"o": o, "v": v}))
            elif line and roll < c.ineffective + 0.15:
                say((correction, {"o": o, "v": (v := mention(value)), "x": current}))
                line.append(v)
                simple[pair] = False
            elif len(line) >= 2 and pair not in undone and roll < c.ineffective + 0.3:  # never undo an undo
                say((rng.choice(UNDO), {"o": o, "s": s}))
                line.append(line[-2])
                simple[pair] = False
                undone.add(pair)
                continue
            else:
                say((rng.choice(sets), {"o": o, "v": (v := mention(value))}))
                line.append(v)
            undone.discard(pair)

        minutes = sorted(rng.sample(range(8 * 60, 18 * 60), len(messages)))
        lines = [(f"[{m // 60:02d}:{m % 60:02d}] {rng.choice(people)}: ", t, kw) for m, (t, kw) in zip(minutes, messages)]
        unordered = rng.random() < c.unordered
        if unordered:
            rng.shuffle(lines)
        doc = Doc().add("Planning chat (one day; messages are " + ("not in time order" if unordered else
                                                                    "in time order") + "). Statements take "
                        "effect when made; proposals only once approved.\n")
        for stamp, template, kw in lines:
            doc.add(stamp + template + "\n", **kw)

        fields, spans = [], {}
        asked = [pair for pair in pairs if pair in touched]
        untouched = [(o, s) for o in plans for s in sorted(SLOTS) if (o, s) not in touched]
        asked += rng.sample(untouched, 1) if untouched and rng.random() < 0.3 else []
        for o, s in asked:
            line = timeline.get((o, s), [])
            name = f"{o.replace(' ', '_')}_{s}"
            fields.append({"name": name, "type": "text", "instruction": f"The {s} of the {o} now in force."})
            spans[name] = doc.marks[line[-1][1]] if line else []
            if simple.get((o, s)) and len(line) >= 2 and rng.random() < c.previous:
                fields.append({"name": name + "_before", "type": "text",
                               "instruction": f"The {s} of the {o} just before its last change."})
                spans[name + "_before"] = doc.marks[line[-2][1]]
        rng.shuffle(fields)
        return extraction_entry(doc.text.strip(), fields, spans, state_seed)
