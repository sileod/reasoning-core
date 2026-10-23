"""Read a value by its place in a document's structure: a section path in an outline, or a cell of one of several
look-alike tables, picked by row and column, by a condition on another column, or by row position.

Latent structure: either an outline (sections, each with subsections holding labeled fields, the same subsection and
field labels recurring under other sections) or several tables of one domain (same columns, different titles such as
sites or years, distinct rows, some empty cells). Every value is distinct, so a span names one place. Questions name
a path (Billing > Contact > Phone), a cell (the revenue of Lima in the 2024 table), a condition (the manager of the
store whose staff count is 14, in the 2024 table) or a position (the third store listed in the 2024 table). The
solver reads the latent place; it is null when the path exists only under another section, the cell is empty, or
the condition holds only in another table, so a look-alike value always sits elsewhere. The renderer writes outlines
as Markdown headings, indented blocks, numbered sections or banner forms, and tables as Markdown, ASCII boxes, CSV,
aligned columns or transposed. Levels add sections or tables, rows, columns, fields, empty cells, missing places,
condition and position queries.
"""
import random
import string
from dataclasses import dataclass
from datetime import date, timedelta

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import CITIES, COMPANIES, FIRST, LAST, Doc, extraction_entry

SECTIONS = ["Billing", "Shipping", "Support", "Sales", "Headquarters", "Warehouse", "Legal", "IT", "Facilities",
            "Human resources"]
SUBSECTIONS = {
    "Contact": ["Name", "Phone", "Email"],
    "Address": ["Street", "City", "Postcode"],
    "Hours": ["Weekdays", "Saturday", "Sunday"],
    "Escalation": ["Manager", "Phone", "Response time"],
}
FIELD_TYPES = {"Name": "person", "Manager": "person", "Phone": "phone", "Email": "email", "Street": "street",
               "City": "city", "Postcode": "postcode", "Weekdays": "hours", "Saturday": "hours", "Sunday": "hours",
               "Response time": "duration"}
# domain: (entity noun, key column, {column: type}, table titles)
DOMAINS = {
    "stores": ("store", "Store", {"Manager": "person", "Opened": "date", "Revenue": "money", "Staff": "count",
                                  "Phone": "phone"}, ["2023", "2024", "2025", "North region", "South region"]),
    "employees": ("employee", "Employee", {"Office": "city", "Start date": "date", "Salary": "money",
                                           "Badge ID": "id", "Desk": "desk"},
                  ["Engineering", "Finance", "Marketing", "Operations"]),
    "shipments": ("shipment", "Shipment", {"Origin": "city", "Shipped": "date", "Weight": "weight",
                                           "Carrier": "company", "Cost": "money"}, ["March", "April", "May", "June"]),
    "servers": ("server", "Host", {"Owner": "person", "IP address": "ip", "CPU load": "percent",
                                   "Uptime": "days", "Patched": "date"},
                ["Cluster A", "Cluster B", "Staging", "Production"]),
}
NOUNS = {"Opened": "opening date", "Staff": "staff count", "Patched": "last patch date", "Shipped": "shipping date",
         "Desk": "desk number", "Weight": "weight", "Cost": "cost", "IP address": "IP address", "CPU load": "CPU load"}
KEYS = {"stores": "store", "employees": "person", "shipments": "id", "servers": "host"}
ORDINALS = ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
            "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth"]
OUTLINES = ["markdown", "indented", "numbered", "banner"]
TABLES = ["markdown", "ascii", "csv", "aligned", "transposed"]
EMPTY = {"markdown": "", "ascii": "", "csv": "", "aligned": "-", "transposed": ""}
STREETS = ["Harbour Road", "Elm Street", "Mill Lane", "Park Lane", "Quay Street", "Station Road"]
HOSTS = ["atlas", "boreas", "cygnus", "draco", "eos", "fornax", "gemini", "hydra", "indus", "juno", "kepler",
         "lyra", "mensa", "norma", "orion", "pavo", "rigel", "sagitta", "tucana", "vega"]


def noun(column):
    return NOUNS.get(column, column if column.isupper() or column.startswith("IP") else column.lower())


def _value(rng, kind, start):
    d = string.digits
    if kind == "person":
        return f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    if kind == "phone":
        return f"+{rng.randint(1, 99)} {rng.randint(100, 999)} {rng.randint(100, 999)} {rng.randint(1000, 9999)}"
    if kind == "email":
        domain = rng.choice(["norvik", "altamar", "pexis", "orrin"])
        return f"{rng.choice(FIRST).lower()}.{rng.choice(LAST).lower()}@{domain}.com"
    if kind == "street":
        return f"{rng.randint(2, 240)} {rng.choice(STREETS)}"
    if kind == "city":
        return rng.choice(CITIES)
    if kind == "store":
        return f"{rng.choice(CITIES)} {rng.choice(['Central', 'North', 'Harbour', 'Airport', 'Old Town', 'Station'])}"
    if kind == "postcode":
        return "".join(rng.choice(d) for _ in range(5))
    if kind == "hours":
        a = rng.randint(6, 11)
        return f"{a:02d}:{rng.choice(['00', '30'])}-{a + rng.randint(4, 10):02d}:{rng.choice(['00', '30'])}"
    if kind == "duration":
        return rng.choice([f"{rng.randint(1, 72)} hours", f"{rng.randint(1, 10)} business days"])
    if kind == "date":
        return (start + timedelta(days=rng.randrange(1500))).isoformat()
    if kind == "money":
        return f"${rng.randint(1_000, 999_999):,}"
    if kind == "count":
        return str(rng.randint(3, 400))
    if kind == "id":
        letters = "".join(rng.choice(string.ascii_uppercase) for _ in range(2))
        return letters + "-" + "".join(rng.choice(d) for _ in range(5))
    if kind == "desk":
        return f"{rng.randint(1, 9)}{rng.choice('ABCDEF')}{rng.randint(1, 40):02d}"
    if kind == "weight":
        return f"{rng.randint(1, 9999)} kg"
    if kind == "company":
        return rng.choice(COMPANIES)
    if kind == "ip":
        return f"10.{rng.randint(0, 255)}.{rng.randint(0, 255)}.{rng.randint(1, 254)}"
    if kind == "percent":
        return f"{rng.randint(1, 99)}%"
    if kind == "days":
        return f"{rng.randint(1, 900)} days"
    if kind == "host":
        return f"{rng.choice(HOSTS)}-{rng.randint(1, 99):02d}"
    raise ValueError(kind)


@dataclass
class StructureLookupExtractionConfig(Config):
    sections: float = 2.0
    tables: float = 2.0
    rows: float = 3.0
    columns: float = 3.0
    fields: float = 2.0
    empty: float = 0.05
    missing: float = 0.15
    condition: float = 0.2
    position: float = 0.1

    def apply_difficulty(self, level):
        self.sections = 2 + 0.75 * level
        self.tables = 2 + 0.5 * level
        self.rows = 3 + 2 * level
        self.columns = 3 + 0.5 * level
        self.fields = 2 + 1.0 * level
        self.empty = 0.05 + 0.025 * level
        self.missing = 0.15 + 0.0625 * level
        self.condition = min(0.5, 0.2 + 0.08 * level)
        self.position = min(0.3, 0.1 + 0.05 * level)


class StructureLookupExtraction(Task):
    summary = ("Read a value by its place: a section path (Billing > Contact > Phone) in an outline whose labels "
               "recur under other sections, or a cell of one of several same-column tables picked by row and "
               "column, a condition on another column or a row position; null when the path, cell or condition "
               "exists only elsewhere. Outlines as headings, indented, numbered or banners; tables as Markdown, "
               "ASCII, CSV, aligned or transposed.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or StructureLookupExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng = random.Random(state_seed)
        used, start = set(), date(2015, 1, 1) + timedelta(days=rng.randrange(2000))

        def fresh(kind):
            for _ in range(200):
                v = _value(rng, kind, start)
                if v not in used:
                    used.add(v)
                    return v
            return None

        if rng.random() < 0.5:
            return self._outline(rng, fresh, state_seed)
        return self._tables(rng, fresh, state_seed)

    def _outline(self, rng, fresh, state_seed):
        c = self.config
        sections = rng.sample(SECTIONS, min(len(SECTIONS), max(2, sround(c.sections, seed=rng.random()))))
        tree = {}
        for s in sections:
            subs = rng.sample(sorted(SUBSECTIONS), rng.randint(1, 3))
            tree[s] = {}
            for sub in subs:
                labels = [f for f in SUBSECTIONS[sub] if rng.random() < 0.75] or SUBSECTIONS[sub][:1]
                tree[s][sub] = {f: v for f in labels if (v := fresh(FIELD_TYPES[f]))}
        places = [(s, sub, f) for s in tree for sub in tree[s] for f in tree[s][sub]]
        # Missing places: a (section, subsection, field) stated under another section only.
        absent = sorted({(s, sub, f) for s in tree for (_, sub, f) in places if f not in tree[s].get(sub, {})})
        asked = []
        for _ in range(max(1, sround(c.fields, seed=rng.random()))):
            pool = absent if absent and rng.random() < c.missing else places
            place = rng.choice(pool)
            if place not in asked:
                asked.append(place)

        style, doc = rng.choice(OUTLINES), Doc()
        doc.add(f"{rng.choice(COMPANIES)} directory\n\n")
        for i, s in enumerate(tree, 1):
            doc.add({"markdown": f"# {s}\n", "indented": f"{s}\n", "numbered": f"{i}. {s}\n",
                     "banner": f"=== {s.upper()} ===\n"}[style])
            for j, sub in enumerate(tree[s], 1):
                doc.add({"markdown": f"## {sub}\n", "indented": f"  {sub}\n", "numbered": f"{i}.{j} {sub}\n",
                         "banner": f"-- {sub} --\n"}[style])
                for f, v in tree[s][sub].items():
                    pad = {"markdown": "- ", "indented": "    ", "numbered": "    ", "banner": ""}[style]
                    doc.add(f"{pad}{f}: {{v}}\n", v=(v, (s, sub, f)))
            doc.add("\n")

        fields, spans = [], {}
        for k, (s, sub, f) in enumerate(asked, 1):
            name = f"{s}_{sub}_{f}".lower().replace(" ", "_")
            instruction = rng.choice(["The {f} under {s} > {sub}.", "In the {s} section, the {sub} {fl}.",
                                      "{s} > {sub} > {f}: the value."]).format(s=s, sub=sub, f=f, fl=f.lower())
            fields.append({"name": name, "type": "text", "instruction": instruction})
            spans[name] = list(doc.marks.get((s, sub, f), []))
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, kind="outline", style=style)

    def _tables(self, rng, fresh, state_seed):
        c = self.config
        domain = rng.choice(sorted(DOMAINS))
        entity, key, columns, titles = DOMAINS[domain]
        cols = rng.sample(sorted(columns), min(len(columns), max(2, sround(c.columns, seed=rng.random()))))
        tables = {}
        for title in rng.sample(titles, min(len(titles), max(1, sround(c.tables, seed=rng.random())))):
            rows = []
            for _ in range(max(2, sround(c.rows, seed=rng.random()))):
                k = fresh(KEYS[domain])
                if k is None:
                    break
                values = {col: None if rng.random() < c.empty else fresh(columns[col]) for col in cols}
                rows.append({key: k, **values})
            if rows:
                tables[title] = rows

        # Queries: (title, row index or None, column, phrase); a row index of None means no row qualifies.
        queries = []
        for _ in range(max(1, sround(c.fields, seed=rng.random()))):
            title = rng.choice(list(tables))
            rows, col = tables[title], rng.choice(cols)
            others = [t for t in tables if t != title]
            r = rng.random()
            if r < c.condition:
                ccol = rng.choice([x for x in cols if x != col] or [key])
                if others and rng.random() < c.missing:  # holds only in another table
                    pool = [row[ccol] for t in others for row in tables[t] if row[ccol]]
                    if not pool:
                        continue
                    i, cval = None, rng.choice(pool)
                else:
                    i = rng.randrange(len(rows))
                    cval = rows[i][ccol]
                    if cval is None:
                        continue
                queries.append((title, i, col, f"the {noun(col)} of the {entity} whose {noun(ccol)} is {cval}"))
            elif r < c.condition + c.position:
                i = rng.randrange(len(rows))
                queries.append((title, i, col, f"the {noun(col)} of the {ORDINALS[i]} {entity} listed"))
            else:
                if others and rng.random() < c.missing:  # the row exists only in another table
                    row = rng.choice([row for t in others for row in tables[t]])
                    queries.append((title, None, col, f"the {noun(col)} of {row[key]}"))
                else:
                    i = rng.randrange(len(rows))
                    queries.append((title, i, col, f"the {noun(col)} of {rows[i][key]}"))

        style, doc = rng.choice(TABLES), Doc()
        header = [key] + cols
        for title, rows in tables.items():
            doc.add(f"{title}\n")
            cells = [[(row[h], (title, n, h)) if row[h] else EMPTY[style] for h in header]
                     for n, row in enumerate(rows)]
            self._table(doc, style, header, cells)
            doc.add("\n")

        fields, spans, seen = [], {}, set()
        for k, (title, i, col, phrase) in enumerate(queries, 1):
            if (title, phrase) in seen:
                continue
            seen.add((title, phrase))
            name = f"{col.lower().replace(' ', '_')}_{k}"
            instruction = rng.choice(["{P}, in the {t} table.", "In the {t} table, {p}.", "{P} ({t})."]).format(
                P=phrase[0].upper() + phrase[1:], p=phrase, t=title)
            fields.append({"name": name, "type": "text", "instruction": instruction})
            spans[name] = [] if i is None else list(doc.marks.get((title, i, col), []))
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, kind="tables", style=style, domain=domain)

    @staticmethod
    def _table(doc, style, header, cells):
        """Cells are plain strings or (value, mark) pairs; padding follows the widest entry of a column."""
        def text(x):
            return x if isinstance(x, str) else x[0]

        lines = ([[h] + [row[k] for row in cells] for k, h in enumerate(header)] if style == "transposed"
                 else [header] + cells)
        width = [max(len(text(x)) for x in column) for column in zip(*lines)]
        sep, left, right = {"markdown": (" | ", "| ", " |"), "ascii": (" | ", "| ", " |"), "csv": (";", "", ""),
                            "aligned": ("  ", "", ""), "transposed": (" | ", "| ", " |")}[style]
        rule = "+" + "+".join("-" * (w + 2) for w in width) + "+\n"
        for n, items in enumerate(lines):
            if style == "ascii" and n in (0, 1):
                doc.add(rule)
            pads = [" " * (width[k] - len(text(x))) if style in ("ascii", "aligned") else ""
                    for k, x in enumerate(items)]
            template = left + sep.join("{c%d}%s" % (k, pads[k]) for k in range(len(items))) + right
            doc.add(template.rstrip() + "\n" if style == "aligned" else template + "\n",
                    **{f"c{k}": x for k, x in enumerate(items)})
            if style == "markdown" and n == 0:
                doc.add("|" + "---|" * len(items) + "\n")
        if style == "ascii":
            doc.add(rule)
