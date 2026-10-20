"""List every order (id or product) meeting a conjunction of conditions after later updates, or name the heaviest.

Orders are introduced as prose, bullets or a table; an update section then cancels, holds, reinstates, reroutes,
reweighs or moves orders to another carrier, so the answer reflects the final state while the spans are the
introductions. Conditions compare destinations, carriers, status and weights (more/less than), some negated; an
empty answer is null. Levels add orders, conditions, updates, negations and near-miss ids.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import CITIES, Doc, extraction_entry

CARRIERS = ["Kestrel Air", "Altamar Freight", "Bluewave Lines", "Polar Cargo", "Rail Nord", "Vela Couriers"]
PRODUCTS = ["olive oil", "copper wire", "coffee beans", "solar panels", "wool", "ceramic tiles", "paper pulp",
            "spare parts", "rice", "glassware", "cork", "steel bolts", "tea", "cotton"]
INTRO = {
    "prose": ["Order {id} carries {w} kg of {p} to {c} with {k}.", "{id}: {w} kg of {p}, shipping to {c} via {k}.",
              "With {k}, order {id} takes {w} kg of {p} to {c}."],
    "bullets": ["- {id}: {p}, {w} kg, to {c}, carrier {k}"],
    "table": ["{id} | {p} | {w} | {c} | {k}"],
}
UPDATES = {
    "status": {"cancelled": ["Order {id} was cancelled.", "{id} is cancelled."],
               "on hold": ["Order {id} is on hold.", "{id} was put on hold at customs."],
               "active": ["Order {id} is active again.", "{id} is back on schedule."]},
    "c": ["Order {id} now ships to {v}.", "{id} was rerouted to {v}."],
    "w": ["The weight of order {id} was corrected to {v} kg.", "{id} actually weighs {v} kg."],
    "k": ["Order {id} moved to carrier {v}.", "{id} now travels with {v}."],
}


def _near_id(key, rng):
    digits = list(key)
    i = rng.randrange(4)
    digits[i] = rng.choice([d for d in "0123456789" if d != digits[i]])
    return "".join(digits)


def _condition(rng, orders, kind, negate):
    """A condition (text, test) on `kind` whose value comes from an order, so it can match."""
    o = rng.choice(orders)
    if kind == "c":
        v = o["c"]
        return (f"does not ship to {v}", lambda x: x["c"] != v) if negate else (f"ships to {v}", lambda x: x["c"] == v)
    if kind == "k":
        v = o["k"]
        return ((f"is not carried by {v}", lambda x: x["k"] != v) if negate else
                (f"is carried by {v}", lambda x: x["k"] == v))
    if kind == "w":
        v = o["w"] + rng.choice([-5, 5])
        return ((f"weighs more than {v} kg", lambda x: x["w"] > v) if rng.random() < 0.5 else
                (f"weighs less than {v} kg", lambda x: x["w"] < v))
    return (("is cancelled or on hold", lambda x: x["status"] != "active") if negate else
            ("is still active", lambda x: x["status"] == "active"))


@dataclass
class ConditionalListExtractionConfig(Config):
    orders: float = 4.0
    conditions: float = 1.0
    updates: float = 0.5
    negation: float = 0.0
    near_ids: float = 0.0
    fields: float = 2.0

    def apply_difficulty(self, level):
        self.orders = 4 + 3 * level
        self.conditions = 1 + 0.5 * level
        self.updates = 0.5 + 1.2 * level
        self.negation = min(0.4, 0.1 * level)
        self.near_ids = min(0.8, 0.2 * level)
        self.fields = 2 + 0.3 * level


class ConditionalListExtraction(Task):
    summary = ("List every order id or product meeting conjunctive (possibly negated, numeric) conditions on "
               "destination, carrier, status and weight after cancellations, reroutes and corrections, or the "
               "heaviest such order; orders given as prose, bullets or a table.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or ConditionalListExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        n = max(3, sround(c.orders, seed=rng.random()))
        ids, base = [], f"{rng.randrange(10_000):04d}"
        while len(ids) < n:
            key = _near_id(base, rng) if rng.random() < c.near_ids else f"{rng.randrange(10_000):04d}"
            if f"K-{key}" not in ids:
                ids.append(f"K-{key}")
        cities, carriers = rng.sample(CITIES, min(4, 2 + n // 4)), rng.sample(CARRIERS, min(4, 2 + n // 5))
        weights = rng.sample(range(10, 400, 5), n)
        orders = [{"id": i, "p": rng.choice(PRODUCTS), "w": w, "c": rng.choice(cities), "k": rng.choice(carriers),
                   "status": "active"} for i, w in zip(ids, weights)]

        style = rng.choice(sorted(INTRO))
        doc = Doc().add("id | product | kg | destination | carrier\n" if style == "table" else "")
        for i, o in enumerate(orders):
            doc.add(rng.choice(INTRO[style]) + ("\n" if style != "prose" else " "),
                    id=(o["id"], f"id{i}"), p=(o["p"], f"p{i}"), w=str(o["w"]), c=o["c"], k=o["k"])
        updates = sround(c.updates, seed=rng.random())
        if updates:
            doc.add("\nLater updates (a cancelled or held order keeps its other details):\n")
        for _ in range(updates):
            o, kind = rng.choice(orders), rng.choice(["status", "status", "c", "w", "k"])
            if kind == "status":
                o["status"] = rng.choice([s for s in UPDATES["status"] if s != o["status"]])
                template = rng.choice(UPDATES["status"][o["status"]])
            else:
                values = {"c": cities, "k": carriers}.get(kind) or [w for w in range(10, 400, 5) if w not in weights]
                o[kind] = rng.choice([v for v in values if v != o[kind]])
                weights.append(o[kind]) if kind == "w" else None
                template = rng.choice(UPDATES[kind])
            doc.add(template + "\n", id=o["id"], v=str(o[kind]))

        fields, spans = [], {}
        for f in range(max(1, sround(c.fields, seed=rng.random()))):
            k, allow_empty = min(4, max(1, sround(c.conditions, seed=rng.random()))), rng.random() < 0.15
            for _ in range(50):  # mostly non-empty: a null list must stay the exception
                conditions = [_condition(rng, orders, kind, rng.random() < c.negation)
                              for kind in rng.sample(["c", "k", "w", "status"], k)]
                match = [i for i, o in enumerate(orders) if all(test(o) for _, test in conditions)]
                if match or allow_empty:
                    break
            phrase = " and ".join(text for text, _ in conditions)
            what = rng.choice(["id", "id", "p", "heaviest"]) if match else "id"
            name = f"{'products' if what == 'p' else 'heaviest' if what == 'heaviest' else 'orders'}_{f + 1}"
            if what == "heaviest":
                match = [max(match, key=lambda i: orders[i]["w"])]
                instruction = f"The id of the heaviest order that {phrase}, after the updates."
            else:
                instruction = (f"Every {'product of an order' if what == 'p' else 'order id'} that {phrase}, "
                               "after the updates.")
            fields.append({"name": name, "type": "text" if what == "heaviest" else "list", "instruction": instruction})
            spans[name] = [span for i in match for span in doc.marks[f"{'p' if what == 'p' else 'id'}{i}"]]
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, style=style)
