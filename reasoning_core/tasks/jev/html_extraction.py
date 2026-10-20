"""Extract fields of the main item from the raw HTML of a product, profile or event page; spans index the source.

Latent structure: a DOM tree whose item scopes are elements of class "item" (the main one has id main-item; related
cards and bundles are items too, nested inside it or in an aside), with hidden content (hidden attribute,
display:none, <template>) and struck-through text (<s>). The solver applies that model: it walks the main scope only
(stopping at nested items), skips hidden content and, for prices, struck text, then follows one relation: dt -> dd,
label for= -> input value, row header -> cell, span.k -> span.v, an element's attribute (data-sku, datetime, href),
or a spec-table cell located under two headers by building the table grid from its rowspan and colspan cells (one
merged cell can answer two queries). No match is null, while decoy scopes state the field. The serializer adds
scripts, navigation and comments. Levels add fields, blocks, decoy cards, nesting, hidden blocks, struck prices,
merged cells, attribute fields and noise.
"""
import random
from dataclasses import dataclass, field

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import CITIES, COMPANIES, FIRST, LAST, MONTHS, Doc, extraction_entry

SAFE = [x for x in COMPANIES if "&" not in x]
ROLES = ["data engineer", "UX researcher", "product manager", "copywriter", "QA lead", "solutions architect"]
VOID = {"input", "meta", "link", "br"}
BLOCK = {"html", "head", "title", "body", "article", "aside", "div", "dl", "dt", "dd", "form", "label", "input", "table",
         "tr", "p", "nav", "footer", "template", "h1", "h2", "h3", "script", "time", "button"}


@dataclass
class El:
    tag: str
    attrs: list = field(default_factory=list)  # (name, value): a value is a string, a (text, mark) leaf or a list
    kids: list = field(default_factory=list)  # El, strings and (text, mark) leaves

    def get(self, name):
        return next((v for k, v in self.attrs if k == name), None)

    def text(self):
        return "".join(k if isinstance(k, str) else k[0] if isinstance(k, tuple) else k.text() for k in self.kids)


def _when(rng):
    m, d = rng.randint(1, 12), rng.randint(1, 28)
    return f"2026-{m:02d}-{d:02d}", f"{d} {MONTHS[m - 1]} 2026"


# family -> item noun, name, labelled fields {label: value}, price label, spec groups and rows, attribute fields
# {name: (tag, class, attribute, prefix, value -> (value, shown text), description)}
FAMILIES = {
    "product": ("product", lambda rng: f"{rng.choice(['Nordic', 'Atlas', 'Vela', 'Kora'])} "
                                       f"{rng.choice(['Desk Lamp', 'Backpack', 'Kettle', 'Speaker', 'Tent'])}",
                {"Brand": lambda rng: rng.choice(SAFE), "Colour": lambda rng: rng.choice(
                    ["graphite", "sand", "forest green", "navy", "coral"]),
                 "Material": lambda rng: rng.choice(["recycled polyester", "oak", "aluminium", "bamboo"]),
                 "Warranty": lambda rng: f"{rng.randint(1, 5)} years"},
                "Price", (["Item", "Package"], {"Width": " cm", "Height": " cm", "Weight": " kg"}),
                {"sku": ("button", "add-to-cart", "data-sku", "",
                         lambda rng: (f"{rng.choice('ABKMT')}{rng.choice('LPRX')}-{rng.randint(1000, 9999)}",
                                      "Add to cart"), "data-sku attribute of the add-to-cart button"),
                 "release": ("time", "release", "datetime", "", _when, "datetime attribute of the release <time> element")}),
    "profile": ("profile", lambda rng: f"{rng.choice(FIRST)} {rng.choice(LAST)}",
                {"Job title": lambda rng: rng.choice(ROLES), "Employer": lambda rng: rng.choice(SAFE),
                 "Location": lambda rng: rng.choice(CITIES),
                 "Phone": lambda rng: f"+44 {rng.randint(7000, 7999)} {rng.randint(100000, 999999)}"},
                None, (["Current role", "Previous role"], {"Company": "", "Title": "", "Team size": ""}),
                {"email": ("a", "contact", "href", "mailto:",
                           lambda rng: (f"{rng.choice(FIRST).lower()}.{rng.choice(LAST).lower()}@example.org",
                                        "Email"), "address in the mailto link (without the mailto: prefix)"),
                 "joined": ("time", "joined", "datetime", "", _when, "datetime attribute of the joined <time> element")}),
    "event": ("event", lambda rng: f"{rng.choice(['Spring', 'Harbour', 'Midnight', 'Winter'])} "
                                   f"{rng.choice(['Jazz Night', 'Film Club', 'Book Fair', 'Food Market'])}",
              {"Venue": lambda rng: f"{rng.choice(['Old Mill', 'Dock 7', 'Town Hall'])}, {rng.choice(CITIES)}",
               "Organizer": lambda rng: rng.choice(SAFE),
               "Capacity": lambda rng: f"{rng.randint(4, 120) * 10} seats"},
              "Ticket price", (["Day 1", "Day 2"], {"Doors": "", "Stage": "", "Headliner": ""}),
              {"start": ("time", "start", "datetime", "", lambda rng: (_when(rng)[0] + f"T{rng.randint(10, 21)}:00",
                                                                      "Starts"), "datetime attribute of the start <time> element"),
               "tickets": ("a", "tickets", "href", "",
                           lambda rng: (f"https://tickets.example.com/e/{rng.randint(10000, 99999)}", "Buy tickets"),
                           "href of the tickets link")}),
}
CELLS = {"Width": lambda rng: str(rng.randint(10, 120)), "Height": lambda rng: str(rng.randint(10, 120)),
         "Weight": lambda rng: f"{rng.randint(2, 90) / 10}", "Company": lambda rng: rng.choice(SAFE),
         "Title": lambda rng: rng.choice(ROLES), "Team size": lambda rng: str(rng.randint(2, 40)),
         "Doors": lambda rng: f"{rng.randint(16, 20)}:{rng.choice(['00', '30'])}",
         "Stage": lambda rng: rng.choice(["Main stage", "Courtyard", "Hall B", "Rooftop"]),
         "Headliner": lambda rng: f"{rng.choice(FIRST)} {rng.choice(LAST)} Trio"}
NOISE = [lambda p: El("script", kids=[f'window.dataLayer = window.dataLayer || []; dataLayer.push({{"page": "{p}"}});']),
         lambda p: El("nav", kids=[El("a", [("href", "/")], ["Home"]), " | ", El("a", [("href", f"/{p}s")], [f"All {p}s"])]),
         lambda p: "<!-- rendered by node-7, cache hit -->",
         lambda p: El("footer", kids=["© 2026 Example Ltd. ", El("a", [("href", "/privacy")], ["Privacy"])]),
         lambda p: El("div", [("class", "cookie-banner")], ["We use cookies. ", El("button", kids=["OK"])]),
         lambda p: El("script", [("src", "/static/vendor.js"), ("defer", None)]),
         lambda p: "<!-- TODO: remove legacy widget -->"]
RULE = "Only the element with id main-item counts, minus nested items, hidden or <template> content and struck text."


# ---- the semantics: scope, visibility, relations, table grid

def scoped(node, hidden=False, struck=False, top=True):
    """(element, hidden, struck) for the elements of the scope rooted at `node`, not entering nested items."""
    if not isinstance(node, El) or (not top and "item" in (node.get("class") or "").split()):
        return
    style = (node.get("style") or "").replace(" ", "")
    hidden = hidden or node.tag == "template" or any(k == "hidden" for k, _ in node.attrs) or "display:none" in style
    struck = struck or node.tag in ("s", "del")
    yield node, hidden, struck
    for kid in node.kids:
        yield from scoped(kid, hidden, struck, False)


def leaves_of(el):
    return [k for k in el.kids if isinstance(k, tuple)]


def labelled(scope, label):
    """The value leaves the visible scope pairs with `label` (dt/dd, label/input, th/td, span.k/span.v)."""
    visible = [e for e, h, _ in scoped(scope) if not h]
    ids = {e.get("id"): e for e in visible if e.get("id")}
    out = []
    for e in visible:
        if e.text().rstrip(":") != label or e.tag not in ("dt", "label", "th", "span"):
            continue
        parent = next((p for p in visible if any(k is e for k in p.kids)), None)
        if e.tag == "label" and e.get("for") in ids:
            out += [p for _, v in ids[e.get("for")].attrs if isinstance(v, tuple) for p in [v]]
        elif parent is not None and e.tag in ("dt", "th", "span"):
            sibs = [k for k in parent.kids if isinstance(k, El)]
            after = sibs[sibs.index(e) + 1:sibs.index(e) + 2]
            want = {"dt": "dd", "th": "td", "span": "span"}[e.tag]
            if after and after[0].tag == want and (e.tag != "th" or "specs" not in str(scope_class(scope, parent))):
                out += leaves_of(after[0])
    return out


def scope_class(scope, row):
    table = next((e for e, _, _ in scoped(scope) if any(k is row for k in e.kids)), None)
    return table.get("class") if table is not None else None


def grid_cell(table, group, row):
    """The td under both headers, on the grid built from rowspan/colspan: its row's th cells and, per column, the
    nearest all-th row above it."""
    grid, rows = {}, [k for k in table.kids if isinstance(k, El) and k.tag == "tr"]
    for r, tr in enumerate(rows):
        col = 0
        for cell in (k for k in tr.kids if isinstance(k, El)):
            while (r, col) in grid:
                col += 1
            rs, cs = int(cell.get("rowspan") or 1), int(cell.get("colspan") or 1)
            for i in range(rs):
                for j in range(cs):
                    grid[r + i, col + j] = cell
            col += cs
    if not grid:
        return []
    width = max(c for _, c in grid) + 1
    header_rows = {r for r in range(len(rows)) if all(grid[r, c].tag == "th" for c in range(width) if (r, c) in grid)}
    hits = []
    for (r, c), cell in grid.items():
        if cell.tag != "td" or cell in hits:
            continue
        heads = {grid[r, k].text() for k in range(width) if (r, k) in grid and grid[r, k].tag == "th"}
        span = [k for k in range(width) if grid.get((r, k)) is cell]
        for k in span:  # the nearest header row above that covers the column
            above = [h for h in header_rows if h < r and (h, k) in grid]
            heads |= {grid[max(above), k].text()} if above else set()
        if {group, row} <= heads:
            hits.append(cell)
    return [leaf for cell in hits for leaf in leaves_of(cell)]


# ---- generation

def _block(kind, pairs, prefix):
    """Labelled values [(label, leaf)] as a dl, a read-only form, a two-column table or key/value spans."""
    if kind == "dl":
        return El("dl", kids=[x for l, v in pairs for x in (El("dt", kids=[l]), El("dd", kids=[v]))])
    if kind == "table":
        return El("table", kids=[El("tr", kids=[El("th", kids=[l]), El("td", kids=[v])]) for l, v in pairs])
    if kind == "form":
        slug = lambda l: f"{prefix}-{l.lower().replace(' ', '-')}"
        return El("form", kids=[x for l, v in pairs for x in (
            El("label", [("for", slug(l))], [l]), El("input", [("id", slug(l)), ("value", v), ("readonly", None)]))])
    return El("div", kids=[El("p", kids=[El("span", [("class", "k")], [l + ":"]), " ", El("span", [("class", "v")], [v])])
                           for l, v in pairs])


def _spec(rng, groups, rows, cell, style, merge):
    """The spec table in one of three layouts; equal neighbours may share one merged cell."""
    def td(v, **span):
        return El("td", [(k, str(n)) for k, n in span.items()], [v] if v else [])
    if style == "columns":
        out = [El("tr", kids=[El("th")] + [El("th", kids=[g]) for g in groups])]
        for r in rows:
            values = [cell(g, r) for g in groups]
            same = merge and values[0] and rng.random() < merge
            out.append(El("tr", kids=[El("th", kids=[r])] + ([td(values[0], colspan=2)] if same else
                                                              [td(v) for v in values])))
        return El("table", [("class", "specs")], out)
    out = []
    for g in groups:
        present = [r for r in rows if cell(g, r) is not None]
        if not present:  # no header without cells
            continue
        if style == "colspan":
            out.append(El("tr", kids=[El("th", [("colspan", "2")], [g])]))
        for k, r in enumerate(present):
            head = [El("th", [("rowspan", str(len(present)))], [g])] if style == "rowspan" and k == 0 else []
            out.append(El("tr", kids=head + [El("th", kids=[r]), td(cell(g, r))]))
    return El("table", [("class", "specs")], out) if out else None


def serialize(node, doc):
    """Write the node; a container of block elements puts each child element and comment on its own line."""
    if not isinstance(node, El):
        return doc.add("{x}", x=node)
    doc.add("{x}", x="<" + node.tag)
    for k, v in node.attrs:
        doc.add("{x}", x=f" {k}" + ("" if v is None else '="'))
        for piece in [] if v is None else v if isinstance(v, list) else [v]:
            doc.add("{x}", x=piece)
        doc.add('"' if v is not None else "")
    doc.add(">")
    if node.tag in VOID:
        return
    nested = any(isinstance(k, El) and k.tag in BLOCK for k in node.kids)
    doc.add("\n" if nested else "")
    for kid in node.kids:
        serialize(kid, doc)
        doc.add("\n" if nested and (isinstance(kid, El) or str(kid).startswith("<!--")) else "")
    doc.add("{x}", x=f"</{node.tag}>")


@dataclass
class HtmlExtractionConfig(Config):
    fields: float = 2.0
    blocks: float = 1.0
    cards: float = 0.5
    nest: float = 0.1
    hidden: float = 0.1
    struck: float = 0.2
    merge: float = 0.1
    attrs: float = 0.15
    missing: float = 0.15
    noise: float = 1.0

    def apply_difficulty(self, level):
        self.fields = 2 + 1.2 * level
        self.blocks = 1 + 0.6 * level
        self.cards = 0.5 + 0.5 * level
        self.nest = min(0.6, 0.1 + 0.12 * level)
        self.hidden = min(0.7, 0.1 + 0.15 * level)
        self.struck = min(0.8, 0.2 + 0.15 * level)
        self.merge = min(0.5, 0.1 + 0.1 * level)
        self.attrs = min(0.5, 0.15 + 0.08 * level)
        self.missing = 0.15 + 0.02 * level
        self.noise = 1 + 1.2 * level


class HtmlExtraction(Task):
    summary = ("Extract the main item's fields from raw HTML of a product, profile or event page by a scope and "
               "visibility model (nested item cards, hidden and template content, struck prices) and relations "
               "(dt/dd, label for, header cells on a rowspan/colspan grid, data-*/datetime/href attributes).")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or HtmlExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        family = rng.choice(sorted(FAMILIES))
        item, name_of, labels, price, (groups, units), attrs = FAMILIES[family]
        count = iter(range(10 ** 6))

        def leaf(text):
            return (text, f"x{next(count)}")

        cells = [(g, r) for g in groups for r in units]
        pool = sorted(labels) + ([price] if price else [])
        asked = []
        for _ in range(min(7, max(2, sround(c.fields, seed=rng.random())))):
            kinds = [sorted(attrs)] if rng.random() < c.attrs else [pool, cells]
            options = [x for x in rng.choice(kinds) if x not in asked]
            options = options or [x for x in pool + cells + sorted(attrs) if x not in asked]
            asked.append(rng.choice(options))
        absent = {x for x in asked if rng.random() < c.missing}

        def content(scope_fields, main):
            """Elements stating the labelled fields, price and attributes of one scope."""
            out, pairs = [], []
            for x in scope_fields:
                if x == price:
                    old = [El("s", kids=[leaf(f"€{rng.randint(900, 49_900) / 100:.2f}")]), " "] \
                        if rng.random() < c.struck else []
                    out.append(El("p", [("class", "price")], [f"{price}: "] + old + [
                        El("span", [("class", "now")], [leaf(f"€{rng.randint(900, 49_900) / 100:.2f}")])]))
                elif x in labels:
                    pairs.append((x, leaf(labels[x](rng))))
                elif x in attrs:
                    tag, cls, attr, prefix, value, _ = attrs[x]
                    v, shown = value(rng)
                    out.append(El(tag, [("class", cls), (attr, [prefix, leaf(v)] if prefix else leaf(v))], [shown]))
            rng.shuffle(pairs)
            k = max(1, min(len(pairs), sround(c.blocks, seed=rng.random()) if main else 1))
            out += [_block(rng.choice(["dl", "table", "form", "p"]), pairs[i::k], f"f{next(count)}")
                    for i in range(k) if pairs[i::k]]
            rng.shuffle(out)
            return out

        everything = pool + sorted(attrs)
        main_fields = [x for x in everything if (x in asked and x not in absent) or
                       (x not in asked and rng.random() < 0.5)]
        main = El("article", [("class", "item main"), ("id", "main-item")], [El("h1", kids=[leaf(name_of(rng))])])
        main.kids += content(main_fields, True)
        if any(x in asked for x in cells) or rng.random() < 0.5:
            values = {x: None if (x in absent or (x not in asked and rng.random() < 0.3)) else
                      leaf(CELLS[x[1]](rng) + units[x[1]]) for x in cells}
            style = rng.choice(["columns", "rowspan", "colspan"])
            table = _spec(rng, groups, list(units), lambda g, r: values[g, r], style,
                          c.merge if style == "columns" else 0)
            if table is not None:
                main.kids.append(table)
        decoys = sorted(set([x for x in everything if x in absent] + rng.sample(everything, 3)), key=everything.index)
        if rng.random() < c.hidden:  # stale values in hidden content of the main scope
            wrap = rng.choice([[("hidden", None)], [("style", "display: none")], None])
            box = El("template" if wrap is None else "div", wrap or [], content(rng.sample(decoys, 2), False))
            main.kids.insert(rng.randint(1, len(main.kids)), box)
        cards = []
        for i in range(sround(c.cards, seed=rng.random()) + any(x in absent for x in everything)):
            while (title := name_of(rng)) == main.kids[0].kids[0][0]:
                pass
            card = El("div", [("class", "item card")], [El("h3", kids=[title])] +
                      content(rng.sample(decoys, rng.randint(1, min(3, len(decoys)))), False))
            if rng.random() < c.nest:  # a bundle nested inside the main item
                main.kids.insert(rng.randint(1, len(main.kids)), card)
            else:
                cards.append(card)

        noise = [n(item) for n in rng.sample(NOISE, min(len(NOISE), sround(c.noise, seed=rng.random())))]
        cut = rng.randint(0, len(noise))
        body = noise[:cut] + [main] + ([El("aside", [("class", "related")], [El("h2", kids=["Related"])] + cards)]
                                       if cards else []) + noise[cut:]
        page = El("html", kids=[El("head", kids=[El("title", kids=[f"{item.title()} | Example"])]),
                                El("body", kids=body)])

        fields, spans = [], {}
        for x in asked:  # the solver reads the DOM: scope, visibility, relation
            if x in cells:
                tables = [e for e, h, _ in scoped(main) if not h and e.tag == "table" and e.get("class") == "specs"]
                hit = [l for t in tables for l in grid_cell(t, *x)]
                name = f"{x[0]}_{x[1]}".lower().replace(" ", "_")
                instruction = (f'The main {item}\'s spec-table cell under both the "{x[0]}" and the "{x[1]}" '
                               f"headers; null if that cell is empty or missing. {RULE}")
            elif x in attrs:
                tag, cls, attr, prefix, _, description = attrs[x]
                hit = [p for e, h, _ in scoped(main) if not h and e.tag == tag and e.get("class") == cls
                       for p in (e.get(attr) if isinstance(e.get(attr), list) else [e.get(attr)]) if
                       isinstance(p, tuple)]
                name, instruction = x, f"The {description} of the main {item}. {RULE}"
            elif x == price:
                boxes = [e for e, h, _ in scoped(main) if not h and e.get("class") == "price"]
                hit = [l for b in boxes for e, _, s in scoped(b) if not s for l in leaves_of(e)]
                name, instruction = "price", f"The current {price.lower()} of the main {item}. {RULE}"
            else:
                hit = labelled(main, x)
                name, instruction = x.lower().replace(" ", "_"), f'The value labelled "{x}" for the main {item}. {RULE}'
            fields.append({"name": name, "type": "text", "instruction": instruction})
            spans[name] = [h[1] for h in hit]

        doc = Doc().add("<!DOCTYPE html>\n")
        serialize(page, doc)
        assert "&" not in doc.text and doc.text.count('"') % 2 == 0
        spans = {n: [s for m in ms for s in doc.marks[m]] for n, ms in spans.items()}
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, family=family)
