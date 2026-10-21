"""List every product of a catalog meeting spec requirements, from specs written in mixed units and layouts.

Latent structure: products with numeric specs in base units (grams, gigabytes, minutes, dollars...), some specs
unstated. Requirements are conjunctions of comparisons (at least, at most, more than, under) whose thresholds sit on
or next to product values and are written in any unit of the spec. Near-miss products copy a matching one and fail
exactly one requirement by a small margin or by leaving that spec unstated, and near-miss names share a model line.
The renderer writes each spec in a unit that keeps it exact (1.5 kg or 1500 g, 2 TB or 2000 GB, 9 h 30 min) as
prose, bullets, key-value blocks or a table. The solver compares base values; an unstated spec does not qualify.
An empty answer is null. Levels add products, requirements, unit variety, near misses and unstated specs; ``scale``
multiplies the product count for long documents.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core import surface_forms as sf
from reasoning_core.tasks.jev._extraction import Doc, article, extraction_entry

# spec: (label, grid in the first unit, units as (symbol, surface_forms dimension or None for a bare suffix; "hm"
# is hours and minutes), phrase for prose, the better direction)
G, H = ("g", "mass"), [("min", "time"), ("h", "time"), ("hm", "time")]
CATEGORIES = {
    "laptop": {
        "weight": ("weight", range(900, 2800, 50), [G, ("kg", "mass")], "weighs {v}", -1),
        "storage": ("storage", [128, 256, 512, 1000, 2000, 4000], [("GB", "data"), ("TB", "data")], "has {v} of storage", 1),
        "memory": ("memory", [8, 16, 24, 32, 64], [("GB", "data")], "has {v} of memory", 1),
        "battery": ("battery life", range(240, 1200, 30), H, "lasts {v} on battery", 1),
        "price": ("price", range(499, 3000, 50), [("$", "money")], "costs {v}", -1),
    },
    "e-bike": {
        "weight": ("weight", range(14000, 32000, 500), [G, ("kg", "mass")], "weighs {v}", -1),
        "range": ("range", range(40, 160, 5), [("km", "length")], "has a range of {v}", 1),
        "battery": ("battery capacity", range(300, 900, 25), [("Wh", "energy"), ("kWh", "energy")], "carries a {v} battery", 1),
        "charge": ("charging time", range(120, 480, 15), H, "charges in {v}", -1),
        "price": ("price", range(1200, 6000, 100), [("$", "money")], "costs {v}", -1),
    },
    "monitor": {
        "size": ("screen size", [24, 27, 32, 34, 38, 43, 49], [("in", "length"), ("cm", "length")], "has a {v} screen", 1),
        "refresh": ("refresh rate", [60, 75, 100, 120, 144, 165, 240], [("Hz", None)], "refreshes at {v}", 1),
        "brightness": ("brightness", range(250, 1000, 50), [("nits", None)], "reaches {v}", 1),
        "weight": ("weight", range(3000, 12000, 100), [G, ("kg", "mass")], "weighs {v}", -1),
        "price": ("price", range(149, 1500, 10), [("$", "money")], "costs {v}", -1),
    },
}
NUMBER_STYLES = ["eu", "si", "swiss"]
BRANDS = ["Norvik", "Altamar", "Pexis", "Quillon", "Halvard", "Kestrel", "Orrin", "Lumen", "Sunvale", "Vela"]
LINES = ["Aero", "Nova", "Flux", "Terra", "Pulse", "Atlas", "Zephyr", "Vertex", "Orbit", "Summit"]
STYLES = ["prose", "bullets", "keyvalue", "table"]
COMPARATORS = {"at least": lambda x, t: x >= t, "at most": lambda x, t: x <= t,
               "more than": lambda x, t: x > t, "under": lambda x, t: x < t}


def write(value, units, rng, variety, style):
    """``value`` (in the first unit) in a random unit that writes it exactly; the first unless ``variety`` draws
    another."""
    first, dimension = units[0]
    options = []
    for unit, dim in units:
        if unit == "hm":
            text = sf.mixed(sf.to_base(value, first, dimension), ["h", "min"], "time", style)
            text = text if text and " min" in text and " h" in text else None
        elif dim is None:
            number = sf.format_number(value, style)
            text = number and f"{number} {unit}"
        else:
            text = sf.render_quantity(sf.to_base(value, first, dimension), unit, dim, style)
        if text:
            options.append(text)
    return options[0] if len(options) == 1 or rng.random() >= variety else rng.choice(options[1:])


@dataclass
class SpecMatchExtractionConfig(Config):
    products: float = 4.0
    scale: float = 1.0
    requirements: float = 1.0
    unit_variety: float = 0.2
    number_style: float = 0.0
    near_misses: float = 1.0
    unstated: float = 0.03
    boundary: float = 0.3
    fields: float = 2.0

    def apply_difficulty(self, level):
        self.products = 4 + 4 * level
        self.requirements = 1 + 0.6 * level
        self.unit_variety = min(0.7, 0.2 + 0.12 * level)
        self.number_style = min(0.5, 0.12 * level)
        self.near_misses = 1 + level
        self.unstated = min(0.1, 0.03 + 0.02 * level)
        self.boundary = min(0.8, 0.3 + 0.12 * level)
        self.fields = 2 + 0.3 * level


class SpecMatchExtraction(Task):
    summary = ("List every laptop, e-bike or monitor of a catalog meeting conjunctive spec requirements (at least, "
               "at most, more than, under) with thresholds in any unit (kg/g, GB/TB, h/min, Wh/kWh), or the best "
               "such product; specs in mixed exact units as prose, bullets, key-value blocks or a table, near-miss "
               "products failing one requirement, unstated specs not qualifying.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or SpecMatchExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        category = rng.choice(sorted(CATEGORIES))
        specs = CATEGORIES[category]
        names = [f"{b} {l} {k}" for b in BRANDS for l in LINES for k in (3, 5, 7, 9, 14, 15, 16)]
        rng.shuffle(names)

        def product():
            return {key: (None if rng.random() < c.unstated else rng.choice(list(grid)))
                    for key, (_, grid, *_) in specs.items()}

        products = [product() for _ in range(max(3, sround(c.products * c.scale, seed=rng.random())))]

        def satisfying(key, comparator, t):
            return [v for v in specs[key][1] if COMPARATORS[comparator](v, t)]

        def meeting(requirements):
            p = product()
            for key, comparator, t in requirements:
                p[key] = rng.choice(satisfying(key, comparator, t))
            return p

        fields, queries = [], []
        for f in range(max(1, sround(c.fields, seed=rng.random()))):
            k = min(len(specs), max(1, sround(c.requirements, seed=rng.random())))
            requirements = []
            for key in rng.sample(sorted(specs), k):
                grid, direction = list(specs[key][1]), specs[key][4]
                values = [p[key] for p in products if p[key] is not None] or grid
                for _ in range(20):  # neither impossible nor true of every grid value
                    value = rng.choice(values)
                    if rng.random() >= c.boundary:  # next to a product value, still on the grid
                        value = grid[max(0, min(len(grid) - 1, grid.index(value) + rng.choice([-1, 1])))]
                    comparator = rng.choice(["at least", "more than"] if direction > 0 else ["at most", "under"])
                    if 0 < len(satisfying(key, comparator, value)) < len(grid):
                        break
                if not satisfying(key, comparator, value):
                    comparator = "at least" if direction > 0 else "at most"
                requirements.append((key, comparator, value))
            queries.append(requirements)
            if rng.random() > 0.3:  # mostly at least one match: a null list stays the exception
                products.append(meeting(requirements))
            for _ in range(sround(c.near_misses, seed=rng.random())):  # meets all requirements but one
                p = meeting(requirements)
                key, comparator, t = rng.choice(requirements)
                failing = [v for v in specs[key][1] if not COMPARATORS[comparator](v, t)]
                p[key] = min(failing, key=lambda v: abs(v - t)) if failing and rng.random() > 0.2 else None
                products.append(p)
        rng.shuffle(products)

        # Names: near-miss names share a model line (Norvik Aero 14 / Norvik Aero 16).
        style, doc = rng.choice(STYLES), Doc()
        numbers = rng.choice(NUMBER_STYLES) if rng.random() < c.number_style else "en"
        rule = sf.NUMBER_STYLES[numbers].convention
        doc.add(f"{category.capitalize()} catalog" + (f" ({rule})" if numbers != "en" else "") + ".\n\n")
        order = sorted(specs)
        if style == "table":
            doc.add("model | " + " | ".join(specs[key][0] for key in order) + "\n")
        line_names = sorted({n.rsplit(" ", 1)[0] for n in names[:len(products)]})
        for i, p in enumerate(products):
            p["name"] = f"{rng.choice(line_names)} {rng.choice([3, 5, 7, 9, 14, 15, 16])}"
            while p["name"] in {q.get("name") for q in products[:i]}:
                p["name"] = names.pop()
            shown = {key: write(p[key], specs[key][2], rng, c.unit_variety, numbers) for key in order if p[key] is not None}
            if style == "table":
                doc.add("{n} | " + " | ".join(shown.get(key, "-") for key in order) + "\n", n=(p["name"], f"n{i}"))
            elif style == "prose":
                stated = [key for key in order if key in shown]
                rng.shuffle(stated)
                clauses = [specs[key][3].format(v=shown[key]) for key in stated]
                text = ", ".join(clauses[:-1]) + (" and " if len(clauses) > 1 else "") + clauses[-1] if clauses else "is listed without specs"
                doc.add("The {n} " + text + ".\n", n=(p["name"], f"n{i}"))
            elif style == "bullets":
                doc.add("- {n}: " + "; ".join(f"{specs[key][0]} {shown[key]}" for key in order if key in shown) + "\n",
                        n=(p["name"], f"n{i}"))
            else:
                doc.add("{n}\n" + "".join(f"  {specs[key][0]}: {shown[key]}\n" for key in order if key in shown) + "\n",
                        n=(p["name"], f"n{i}"))

        spans = {}
        for f, requirements in enumerate(queries):
            phrase = " and ".join(f"{specs[key][0]} {comparator} {write(t, specs[key][2], rng, c.unit_variety, numbers)}"
                                  for key, comparator, t in requirements)
            match = [i for i, p in enumerate(products)
                     if all(p[key] is not None and COMPARATORS[cmp](p[key], t) for key, cmp, t in requirements)]
            best = rng.choice(sorted(specs))
            direction = specs[best][4]
            ranked = sorted((p[best] * direction for i, p in enumerate(products) if i in match and p[best] is not None),
                            reverse=True)
            if match and rng.random() < 0.25 and ranked and ranked[:2].count(ranked[0]) == 1:
                pick = next(i for i in match if products[i][best] is not None and products[i][best] * direction == ranked[0])
                word = {"weight": "lightest", "price": "cheapest", "charge": "fastest-charging"}.get(
                    best, f"one with the {'lowest' if direction < 0 else 'highest'} {specs[best][0]}")
                word = word if word.startswith("one") else f"{word} one"
                name = f"best_{f + 1}"
                instruction = (f"Among the {category}s with {phrase}, the {word}. "
                               f"{article(category).capitalize()} {category} whose spec is not given does not qualify.")
                match = [pick]
            else:
                name = f"{category.replace('-', '')}s_{f + 1}"
                instruction = (f"Every {category} with {phrase}. {article(category).capitalize()} {category} whose "
                               "spec is not given does not qualify.")
            fields.append({"name": name, "type": "text" if name.startswith("best") else "list",
                           "instruction": instruction})
            spans[name] = [span for i in match for span in doc.marks[f"n{i}"]]
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, style=style, category=category, numbers=numbers)
