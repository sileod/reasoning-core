"""Read a short story in which people move between cities, change jobs and hand objects to each other, then write
the final state of everyone as a sorted table, one line per person: `Name: city, job, objects`.

Facts are stated once and then updated, sometimes through relations ("moved to the city where X lives", "took
the same job as Y"), so the table requires tracking state over natural language; every field is checked.
Level adds people, events and relative references.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround

NAMES = ["Ana", "Ben", "Chloe", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jade", "Kai", "Lena"]
CITIES = ["Lyon", "Porto", "Oslo", "Riga", "Kyoto", "Lima", "Quito", "Perth", "Turin", "Ghent"]
JOBS = ["baker", "nurse", "pilot", "tailor", "chemist", "judge", "farmer", "editor", "plumber", "teacher"]
OBJECTS = ["a lamp", "a violin", "a map", "a kettle", "a bicycle", "a clock", "a camera", "a globe"]


@dataclass
class NarrativeStateTableConfig(Config):
    n_people: float = 2
    n_events: float = 2
    relative_p: float = 0.2

    def apply_difficulty(self, level):
        self.n_people += 0.6 * level
        self.n_events += 1.5 * level
        self.relative_p = min(0.6, self.relative_p + 0.07 * level)


def _a(word):
    return f"an {word}" if word[0] in "aeiou" else f"a {word}"


def _event(rng, state, rel_p):
    """One update sentence; mutates state."""
    p = rng.choice(list(state))
    others = [q for q in state if q != p]
    kind = rng.choice(["move", "job", "give"] if any(state[q]["objects"] for q in state) else ["move", "job"])
    if kind == "move":
        if others and rng.random() < rel_p:
            q = rng.choice(others)
            if state[q]["city"] != state[p]["city"]:
                state[p]["city"] = state[q]["city"]
                return f"{p} moved to the city where {q} lives."
        city = rng.choice([c for c in CITIES if c != state[p]["city"]])
        state[p]["city"] = city
        return f"{p} moved to {city}."
    if kind == "job":
        if others and rng.random() < rel_p:
            q = rng.choice(others)
            if state[q]["job"] != state[p]["job"]:
                state[p]["job"] = state[q]["job"]
                return f"{p} took the same job as {q}."
        job = rng.choice([j for j in JOBS if j != state[p]["job"]])
        state[p]["job"] = job
        return f"{p} became {_a(job)}."
    giver = rng.choice([q for q in state if state[q]["objects"]])
    taker = rng.choice([q for q in state if q != giver])
    obj = rng.choice(state[giver]["objects"])
    state[giver]["objects"].remove(obj)
    state[taker]["objects"].append(obj)
    return f"{giver} gave {obj} to {taker}."


def _table(state):
    return "\n".join(f"{p}: {s['city']}, {s['job']}, {' and '.join(sorted(s['objects'])) or 'nothing'}"
                     for p, s in sorted(state.items()))


class NarrativeStateTable(DevTask):
    summary = ("Track people's cities, jobs and objects through a story of moves, job changes and hand-overs "
               "(some stated relative to another person) and write everyone's final state as a sorted one-line-per-"
               "person table.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or NarrativeStateTableConfig())

    def generate_entry(self):
        c, rng = self.config, random
        people = rng.sample(NAMES, min(len(NAMES), max(2, sround(c.n_people))))
        objs = rng.sample(OBJECTS, min(len(OBJECTS), len(people)))
        state = {p: {"city": rng.choice(CITIES), "job": rng.choice(JOBS), "objects": []} for p in people}
        for o in objs:
            state[rng.choice(people)]["objects"].append(o)
        intro = [f"{p} is {_a(s['job'])} in {s['city']}" + (f" who owns {' and '.join(s['objects'])}" if s["objects"] else "")
                 + "." for p, s in state.items()]
        events = [_event(rng, state, c.relative_p) for _ in range(max(1, sround(c.n_events)))]
        return Entry({"story": " ".join(intro + ["Then:"] + events)}, _table(state))

    def render_prompt(self, m):
        return (f"{m['story']}\nWrite everyone's final state, one line per person in alphabetical order, formatted "
                "exactly as `Name: city, job, objects` (objects in alphabetical order joined by \" and \", or "
                "\"nothing\").")

    def score_answer(self, answer, entry):
        norm = lambda s: [" ".join(line.split()) for line in str(s).strip().strip("`").splitlines() if line.strip()]
        return float(norm(answer) == norm(entry.answer))
