"""List every record whose date of a given role falls in a range, from dates written in many formats.

Latent structure: records (an id and two dated roles, e.g. issued and due) on a calendar. The renderer groups them
into sections, each with a stated convention (ISO, day/month/year, month/day/year, or a stated year that its dates
omit), and writes every date in a format allowed by its section: numeric, day-month or month-day words, with or
without weekday, or relative to another record's date ("three days after INV-2041 was issued"). Queries are ranges
(inclusive or exclusive bounds), before/after a date, a month or a weekday, on one role, or the earliest/latest such
record; bounds sit on or next to record dates, so off-by-one readings fail. The solver compares calendar dates. An
empty answer is null. Levels add records, sections with numeric conventions, omitted years, relative dates, weekday
queries and boundary dates; ``scale`` multiplies the record count for long documents.
"""
import datetime
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import MONTHS, Doc, extraction_entry

DOMAINS = [
    ("invoice", "INV", ("issued", "due"), "Invoice {id} was issued {d0} and is due {d1}."),
    ("shipment", "SHP", ("shipped", "delivered"), "Shipment {id} was shipped {d0} and delivered {d1}."),
    ("contract", "CTR", ("signed", "renewed"), "Contract {id} was signed {d0} and renewed {d1}."),
    ("ticket", "TCK", ("opened", "closed"), "Ticket {id} was opened {d0} and closed {d1}."),
]
LINES = {"prose": "{text} ", "bullets": "- {text}\n"}
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
NUMBERS = [None, "one day", "two days", "three days", "four days", "five days", "six days", "a week"]
# A section's convention decides which formats its dates may use.
CONVENTIONS = {
    "iso": "numeric dates are year-month-day",
    "dmy": "numeric dates are day/month/year",
    "mdy": "numeric dates are month/day/year",
    "year": "dates without a year are in {year}",
}


def render(day, convention, rng, weekday):
    """``day`` in a format allowed by ``convention``."""
    d, m, y = day.day, MONTHS[day.month - 1], day.year
    words = rng.choice([f"{d} {m} {y}", f"{m} {d}, {y}", f"{d} {m[:3]} {y}"])
    text = {"iso": lambda: rng.choice([day.isoformat(), words]),
            "dmy": lambda: rng.choice([f"{d:02d}/{day.month:02d}/{y}", f"{d}/{day.month}/{y}", words]),
            "mdy": lambda: rng.choice([f"{day.month:02d}/{d:02d}/{y}", f"{day.month}/{d}/{y}", words]),
            "year": lambda: rng.choice([f"{d} {m}", f"{m} {d}"])}[convention]()
    return f"{WEEKDAYS[day.weekday()]} {text}" if weekday else text


def plain(day):
    """A query bound: unambiguous in any section."""
    return f"{day.day} {MONTHS[day.month - 1]} {day.year}"


@dataclass
class DateRangeExtractionConfig(Config):
    records: float = 5.0
    scale: float = 1.0
    sections: float = 1.0
    numeric: float = 0.0
    no_year: float = 0.0
    relative: float = 0.0
    weekday_query: float = 0.0
    boundary: float = 0.3
    fields: float = 2.0

    def apply_difficulty(self, level):
        self.records = 5 + 5 * level
        self.sections = 1 + 0.6 * level
        self.numeric = min(0.6, 0.15 * level)
        self.no_year = min(0.3, 0.08 * level)
        self.relative = min(0.3, 0.08 * level)
        self.weekday_query = min(0.15, 0.04 * level)
        self.boundary = min(0.8, 0.3 + 0.12 * level)
        self.fields = 2 + 0.3 * level


class DateRangeExtraction(Task):
    summary = ("List every record (invoice, shipment, contract, ticket) whose date of one role falls in a range, "
               "before or after a date, in a month or on a weekday, or the earliest/latest one; dates are ISO, "
               "day/month or month/day numeric under a stated section convention, worded, year-less under a stated "
               "year, or relative to another record.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or DateRangeExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        kind, prefix, roles, template = rng.choice(DOMAINS)
        n = max(3, sround(c.records * c.scale, seed=rng.random()))
        year = rng.randrange(2015, 2031)
        start = datetime.date(year, 1, 1) + datetime.timedelta(days=rng.randrange(200))
        span = max(20, 3 * n)  # dense enough that ranges hold several records and boundaries collide
        ids = [f"{prefix}-{k}" for k in rng.sample(range(1000, 10_000), n)]
        records = []
        for i in ids:
            d0 = start + datetime.timedelta(days=rng.randrange(span))
            records.append({"id": i, "dates": [d0, d0 + datetime.timedelta(days=rng.randrange(1, 40))]})

        # Sections: each has a convention; a year-less section only holds records of its own year.
        k = min(n, max(1, sround(c.sections, seed=rng.random())))
        conventions = []
        for _ in range(k):
            r = rng.random()
            conventions.append(rng.choice(["dmy", "mdy"]) if r < c.numeric else
                               "year" if r < c.numeric + c.no_year else "iso")
        order = list(range(n))
        rng.shuffle(order)
        cuts = sorted(rng.sample(range(1, n), k - 1)) if k > 1 else []
        groups = [order[a:b] for a, b in zip([0] + cuts, cuts + [n])]

        style, doc, written = rng.choice(sorted(LINES)), Doc(), set()
        doc.add(f"{kind.capitalize()} register.\n")
        for g, (convention, group) in enumerate(zip(conventions, groups)):
            if convention == "year" and any(d.year != year for i in group for d in records[i]["dates"]):
                convention = "iso"
            rule = CONVENTIONS[convention].format(year=year)
            doc.add(f"\nSection {g + 1} ({rule}):\n")
            for i in group:
                r, parts = records[i], []
                for role, day in zip(roles, r["dates"]):
                    anchors = [(j, q) for j in written for q in range(2) if 0 < (day - records[j]["dates"][q]).days < len(NUMBERS)]
                    if anchors and rng.random() < c.relative:
                        j, q = rng.choice(anchors)
                        gap = (day - records[j]["dates"][q]).days
                        parts.append(f"{NUMBERS[gap]} after {records[j]['id']} was {roles[q]}")
                    else:
                        parts.append("on " + render(day, convention, rng, rng.random() < 0.2))
                line = template.format(id="\0", d0=parts[0], d1=parts[1])
                head, tail = line.split("\0")
                doc.add(LINES[style].replace("{text}", "{h}{id}{t}"), h=head, id=(r["id"], f"id{i}"), t=tail)
                written.add(i)

        fields, spans = [], {}
        for f in range(max(1, sround(c.fields, seed=rng.random()))):
            q, allow_empty = rng.randrange(2), rng.random() < 0.15
            for _ in range(50):
                phrase, test = self._query(rng, records, q, c)
                match = [i for i, r in enumerate(records) if test(r["dates"][q])]
                if match or allow_empty:
                    break
            what = rng.choice(["all", "all", "all", "earliest", "latest"]) if match else "all"
            if what == "all":
                name, instruction = f"{kind}s_{f + 1}", f"Every {kind} id {roles[q]} {phrase}."
            else:
                pick = (min if what == "earliest" else max)(match, key=lambda i: (records[i]["dates"][q], i))
                if sum(records[i]["dates"][q] == records[pick]["dates"][q] for i in match) > 1:
                    name, instruction = f"{kind}s_{f + 1}", f"Every {kind} id {roles[q]} {phrase}."
                else:
                    match = [pick]
                    name = f"{what}_{f + 1}"
                    instruction = f"The id of the {kind} {roles[q]} {what} among those {roles[q]} {phrase}."
            fields.append({"name": name, "type": "list" if name.startswith(kind) else "text",
                           "instruction": instruction})
            spans[name] = [span for i in match for span in doc.marks[f"id{i}"]]
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, style=style,
                                conventions=conventions)

    @staticmethod
    def _query(rng, records, q, c):
        """A (phrase, test) on the date of role ``q``; bounds come from record dates, sometimes shifted by a day."""
        def bound():
            day = rng.choice(records)["dates"][rng.randrange(2)]
            return day if rng.random() < c.boundary else day + datetime.timedelta(days=rng.choice([-1, 1]))

        if rng.random() < c.weekday_query:
            w = rng.choice(sorted({r["dates"][q].weekday() for r in records}))
            return f"on a {WEEKDAYS[w]}", lambda d: d.weekday() == w
        kind = rng.choice(["between", "between", "between", "before", "after", "month"])
        if kind == "month":
            day = rng.choice(records)["dates"][q]
            return (f"in {MONTHS[day.month - 1]} {day.year}",
                    lambda d: (d.year, d.month) == (day.year, day.month))
        if kind == "before":
            day, strict = bound(), rng.random() < 0.5
            return ((f"before {plain(day)}", lambda d: d < day) if strict else
                    (f"on or before {plain(day)}", lambda d: d <= day))
        if kind == "after":
            day, strict = bound(), rng.random() < 0.5
            return ((f"after {plain(day)}", lambda d: d > day) if strict else
                    (f"on or after {plain(day)}", lambda d: d >= day))
        a, b = sorted([bound(), bound()])
        if rng.random() < 0.5:
            return f"between {plain(a)} and {plain(b)}, both included", lambda d: a <= d <= b
        return f"strictly after {plain(a)} and strictly before {plain(b)}", lambda d: a < d < b
