"""Tag every mention of each requested type, as named-entity recognition does, where the type is decided by
context or by a stated definition rather than by the surface form.

Three families, drawn uniformly at every level: context-typed mentions (one name, e.g. Jordan, is a person, a
place, an organization or a product depending on its sentence; unrequested types are distractors); role types
defined in the field (every mention of a company that currently supplies, buys from or partners with a given
company, among relations between other companies and former or failed ones); and pattern-defined codes (ticket
ids, order numbers, versions... described in the field, among near-miss strings). Levels scale mentions, requested
types, ambiguous names, sentences with two mentions, short references (surname, a company's first word),
indirect role statements, distracting relations and near misses.
"""
import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import CITIES, COMPANIES, FIRST, LAST, Doc, extraction_entry

AMBIGUOUS = ["Jordan", "Victoria", "Austin", "Florence", "Phoenix", "Sydney", "Chelsea", "Lincoln", "Hudson",
             "Georgia", "Dallas", "Orion", "Atlas", "Aurora", "Sterling", "Logan", "Savannah", "Camden"]
PRODUCTS = ["Nimbus X2", "Quill Pad", "Halo Buds", "Vertex 9", "Pebble Hub", "Lumo Lamp", "Arc Router", "Tidy Vac"]
POOLS = {"person": [f"{f} {l}" for f in FIRST for l in LAST], "place": CITIES, "organization": COMPANIES,
         "product": PRODUCTS}
FRAMES = {
    "person": ["{x} signed the agreement on Monday.", "According to {x}, the delay was minor.",
               "{x} was promoted to team lead.", "I asked {x} to review the draft.", "{x} said she would call back."],
    "place": ["The team flew to {x} on Tuesday.", "Rents in {x} rose sharply this year.",
              "The office in downtown {x} is closing.", "Heavy snow closed the roads around {x}."],
    "organization": ["Shares of {x} fell three percent.", "The board of {x} approved the merger.",
                     "{x} announced its quarterly earnings.", "Regulators fined {x} for late filings."],
    "product": ["The latest {x} release fixed the battery drain.", "A firmware update for the {x} is available.",
                "Reviewers praised the {x} for its price.", "We returned two faulty {x} units."],
}
COMBOS = [("person", "place", "{x} moved to {y} last spring."), ("person", "organization", "{x} joined {y} as an analyst."),
          ("organization", "place", "{x} opened a plant near {y}."), ("person", "product", "{x} reviewed the {y} for our blog."),
          ("organization", "product", "{x} recalled the {y} after complaints."),
          ("place", "organization", "Back in {x}, {y} is the largest employer.")]
TYPE_TEXT = {"person": "a person", "place": "a place (city, region or country)",
             "organization": "an organization (company, agency or institution)", "product": "a product"}

ROLES = {  # role -> current relation templates ({x} the other company, {u} the reference company)
    "supplier": ["{x} ships components to {u}.", "{u} buys its packaging from {x}.", "{x} has supplied {u} since 2019."],
    "client": ["{u} sells its sensors to {x}.", "{x} is a long-standing customer of {u}.", "{x} placed a new order with {u}."],
    "partner": ["{u} and {x} co-develop a new platform.", "{x} partners with {u} on battery research."],
}
FORMER = {
    "supplier": ["{x} used to supply {u} but stopped last year.", "{x} bid to supply {u} but lost the tender."],
    "client": ["{u} no longer sells to {x}.", "{x} cancelled its contract with {u} in March."],
    "partner": ["{x} ended its joint project with {u}.", "Talks about a partnership between {u} and {x} failed."],
}
INDIRECT = {  # current relations stated from the other side or as a description
    "supplier": ["{u}'s main supplier of steel is {x}.", "Most parts in {u}'s new line come from {x}.",
                 "Without deliveries from {x}, {u}'s plant would stop."],
    "client": ["{x} relies on {u} for its sensors.", "Orders from {x} make up a third of {u}'s revenue.",
               "{x} renewed its yearly purchase contract with {u}."],
    "partner": ["{x} is {u}'s co-developer on the new platform.", "Engineers from {x} and {u} share a lab."],
}
ROLE_TEXT = {"supplier": "currently supplies goods to {u}", "client": "currently buys from {u}",
             "partner": "currently develops products jointly with {u}"}
OTHER = ["{x} ships components to {y}.", "{y} is a long-standing customer of {x}.", "{x} and {y} co-develop a sensor.",
         "{x} is suing {y} over a patent."]


def _digits(rng, n):
    return "".join(rng.choice("0123456789") for _ in range(n))


def _letters(rng, n):
    return "".join(rng.choice("ABCDEFGHJKLMNPQRSTUVWXYZ") for _ in range(n))


# code type -> (description, pattern, valid(rng), near misses(rng)) ; near misses are re-checked against every pattern
CODES = {
    "ticket_id": ("two capital letters, a dash and four digits, e.g. QX-4821", r"[A-Z]{2}-\d{4}",
                  lambda r: f"{_letters(r, 2)}-{_digits(r, 4)}",
                  lambda r: rng_pick(r, [f"{_letters(r, 2)}-{_digits(r, 3)}", f"{_letters(r, 3)}-{_digits(r, 4)}",
                                         f"{_letters(r, 2).lower()}-{_digits(r, 4)}", f"{_letters(r, 2)}{_digits(r, 4)}",
                                         f"{_letters(r, 2)}-{_digits(r, 5)}"])),
    "order_number": ("ORD followed by exactly six digits, e.g. ORD204611", r"ORD\d{6}",
                     lambda r: f"ORD{_digits(r, 6)}",
                     lambda r: rng_pick(r, [f"ORD-{_digits(r, 6)}", f"ORD{_digits(r, 5)}", f"ORD{_digits(r, 7)}",
                                            f"ord{_digits(r, 6)}", f"OD{_digits(r, 6)}"])),
    "invoice_id": ("INV, a dash, four digits, a dash and three digits, e.g. INV-2024-117", r"INV-\d{4}-\d{3}",
                   lambda r: f"INV-{_digits(r, 4)}-{_digits(r, 3)}",
                   lambda r: rng_pick(r, [f"INV-{_digits(r, 3)}-{_digits(r, 4)}", f"INV{_digits(r, 4)}-{_digits(r, 3)}",
                                          f"INV-{_digits(r, 4)}-{_digits(r, 2)}", f"IVN-{_digits(r, 4)}-{_digits(r, 3)}"])),
    "version": ("a lowercase v and three dot-separated numbers, e.g. v2.10.3", r"v\d{1,2}\.\d{1,2}\.\d{1,2}",
                lambda r: f"v{r.randint(0, 12)}.{r.randint(0, 20)}.{r.randint(0, 20)}",
                lambda r: rng_pick(r, [f"v{r.randint(0, 12)}.{r.randint(0, 20)}", f"{r.randint(0, 12)}.{r.randint(0, 20)}.{r.randint(0, 9)}",
                                       f"V{r.randint(0, 12)}.{r.randint(0, 20)}.{r.randint(0, 9)}",
                                       f"v{r.randint(0, 9)}.{r.randint(0, 9)}.{r.randint(0, 9)}.{r.randint(0, 9)}"])),
    "iso_date": ("a date written YYYY-MM-DD with a real month and day, e.g. 2024-03-09", r"20\d\d-(0[1-9]|1[0-2])-(0[1-9]|1\d|2[0-8])",
                 lambda r: f"20{_digits(r, 2)}-{r.randint(1, 12):02d}-{r.randint(1, 28):02d}",
                 lambda r: rng_pick(r, [f"20{_digits(r, 2)}/{r.randint(1, 12):02d}/{r.randint(1, 28):02d}",
                                        f"20{_digits(r, 2)}-{r.randint(13, 19)}-{r.randint(1, 28):02d}",
                                        f"20{_digits(r, 2)}-{r.randint(1, 9)}-{r.randint(1, 9)}",
                                        f"{r.randint(1, 28):02d}-{r.randint(1, 12):02d}-20{_digits(r, 2)}"])),
}
CARRIERS = ["Please check {c} before Friday.", "Reference {c} appears twice in the logs.", "See {c} for details.",
            "{c} was updated by the night shift.", "The customer quoted {c} on the phone.", "Escalate {c} if it fails again."]


def rng_pick(rng, options):
    return rng.choice(options)


def _shortener(rng, p, names, kind):
    """After a first full mention, a person by surname or a company by its first word, with probability p, when
    that short form is unambiguous among the text's names."""
    seen = set()
    def ref(x):
        words = x.split()
        short = words[-1] if kind(x) == "person" else words[0]
        ok = len(words) > 1 and kind(x) in ("person", "organization") and \
            sum(short in n.split() for n in names) == 1 and short not in AMBIGUOUS
        out = short if ok and x in seen and rng.random() < p else x
        seen.add(x)
        return out
    return ref


def _context_typed(rng, c, doc):
    types = sorted(POOLS)
    asked = rng.sample(types, min(len(types), max(1, sround(c.types, seed=rng.random()))))
    present = [t for t in types if rng.random() >= c.absent] or [rng.choice(types)]
    names = rng.sample(AMBIGUOUS, 3)  # few ambiguous names per text, so one name takes several types
    pick = lambda t: rng.choice(names) if rng.random() < c.ambiguity else rng.choice(POOLS[t])
    sentences, n = [], max(2, sround(c.mentions, seed=rng.random()))
    while sum(len(m) for _, m in sentences) < n:
        combos = [k for k in COMBOS if k[0] in present and k[1] in present]
        if combos and rng.random() < c.combo:
            t1, t2, frame = rng.choice(combos)
            x, y = pick(t1), pick(t2)
            if x != y:
                sentences.append((frame, [(x, t1), (y, t2)]))
        else:
            t = rng.choice(present)
            sentences.append((rng.choice(FRAMES[t]), [(pick(t), t)]))
    kinds = {x: t for _, m in sentences for x, t in m}
    ref = _shortener(rng, c.short_refs, list(kinds), kinds.get)
    for frame, mentions in sentences:
        doc.add(frame + " ", **{k: (ref(x), t) for k, (x, t) in zip("xy", mentions)})
    return [{"name": t, "type": "list", "instruction": f"Every mention of {TYPE_TEXT[t]}, as written."}
            for t in asked], {t: doc.marks.get(t, []) for t in asked}


def _defined_roles(rng, c, doc):
    us, *others = rng.sample(COMPANIES, min(len(COMPANIES), 3 + sround(c.mentions / 2, seed=rng.random())))
    asked = rng.sample(sorted(ROLES), min(len(ROLES), max(1, sround(c.types, seed=rng.random()))))
    role_of = {x: rng.choice(sorted(ROLES)) for x in others if rng.random() >= c.ambiguity}  # the rest: no relation
    sentences = [(rng.choice(INDIRECT[r] if rng.random() < c.indirect else ROLES[r]), x, None) for x, r in role_of.items()]
    for _ in range(sround(c.mentions * c.ambiguity, seed=rng.random())):  # relations that do not make a role
        x, y = rng.sample(others, 2)
        if rng.random() < c.former:
            r = rng.choice(sorted(ROLES))
            if role_of.get(x) != r:
                sentences.append((rng.choice(FORMER[r]), x, None))
        else:
            sentences.append((rng.choice(OTHER), x, y))
    rng.shuffle(sentences)
    ref = _shortener(rng, c.short_refs, [us] + others, lambda x: "organization")
    for template, x, y in sentences:
        doc.add(template + " ", u=ref(us), x=(ref(x), f"co:{x}"), y=(ref(y) if y else "", f"co:{y}" if y else None))
    spans = {r: [s for x, role in role_of.items() if role == r for s in doc.marks.get(f"co:{x}", [])] for r in asked}
    return [{"name": f"{r}s", "type": "list", "instruction": f"Every mention of a company that "
             f"{ROLE_TEXT[r].format(u=us)}, as written."} for r in asked], {f"{r}s": spans[r] for r in asked}


def _pattern_codes(rng, c, doc):
    asked = rng.sample(sorted(CODES), min(len(CODES), max(1, sround(c.types, seed=rng.random()))))
    patterns = [re.compile(p) for _, p, _, _ in CODES.values()]
    present = [k for k in asked if rng.random() >= c.absent]
    for _ in range(max(2, sround(c.mentions, seed=rng.random()))):
        k = rng.choice(asked)
        if k in present and rng.random() >= c.near_miss:
            code, mark = CODES[k][2](rng), k
        else:
            code = CODES[k][3](rng)
            if any(p.fullmatch(code) for p in patterns):
                continue
            mark = None
        doc.add(rng.choice(CARRIERS) + " ", c=(code, mark))
    return [{"name": k + "s", "type": "list", "instruction": f"Every {k.replace('_', ' ').replace('iso', 'ISO')} ({CODES[k][0]}), as a whole "
             "token written exactly in this format; strings that differ from it do not count."} for k in asked], \
        {k + "s": doc.marks.get(k, []) for k in asked}


FAMILIES = {"context_typed": _context_typed, "defined_roles": _defined_roles, "pattern_codes": _pattern_codes}


@dataclass
class TypedMentionExtractionConfig(Config):
    mentions: float = 4.0
    types: float = 2.0
    ambiguity: float = 0.15
    former: float = 0.0
    near_miss: float = 0.0
    absent: float = 0.15
    short_refs: float = 0.0
    combo: float = 0.0
    indirect: float = 0.0

    def apply_difficulty(self, level):
        self.mentions = 4 + 3 * level
        self.types = 2 + 0.5 * level
        self.ambiguity = min(0.5, 0.15 + 0.1 * level)
        self.former = min(0.5, 0.1 * level)
        self.near_miss = min(0.6, 0.15 * level)
        self.short_refs = min(0.7, 0.2 * level)
        self.combo = min(0.7, 0.2 * level)
        self.indirect = min(0.7, 0.2 * level)


class TypedMentionExtraction(Task):
    summary = ("Tag every mention of each requested type, NER-style: context-typed names shared by people, places, "
               "organizations and products; companies by a defined current role among other and former relations; "
               "and codes defined by a stated format among near-miss strings.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or TypedMentionExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng = random.Random(state_seed)
        family = rng.choice(sorted(FAMILIES))
        doc = Doc()
        fields, spans = FAMILIES[family](rng, self.config, doc)
        if not doc.text.strip():
            return None
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, family=family)
