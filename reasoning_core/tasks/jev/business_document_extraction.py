"""Read the value in force on a date from an invoice, purchase order, contract or insurance policy with amendments.

Latent structure: typed facts (key, location, rank, validity interval, value or reference). A location is the body or
a schedule; printed facts have rank 0 and numbered amendments (corrections, changes, endorsements) rank 1, 2, ...;
an interval is the whole term, a dated window, or an amendment's effective date onward (or to its end date). The
solver resolves (key, date) at the body: among the facts there whose interval contains the date, the highest rank
wins, and a reference ("see Schedule B") resolves the same key and date in that schedule, so chains run through
schedules and amendments override printed values, earlier amendments, references and schedule entries. Nothing live
is null, while a near-miss key (subtotal for total, invoice date for due date) is stated. The document states the
precedence rule; the renderer only words facts as label lines, dated windows, schedules and numbered amendments.
Levels add keys, near-miss keys, windows, amendments, amendments stacking on one key, reference chains and
amendments listed out of order.
"""
import random
from dataclasses import dataclass
from datetime import date, timedelta

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import CITIES, COMPANIES, FIRST, LAST, MONTHS, Doc, extraction_entry

STREETS = ["Harbour Road", "Elm Street", "Rue des Lilas", "Kings Avenue", "Mill Lane", "Via Roma", "Calle Mayor"]
GEN = {
    "date": lambda rng, cur: _fmt(date(2025, 1, 1) + timedelta(days=rng.randrange(730))),
    "money": lambda rng, cur: f"{cur}{rng.randint(80_00, 9000_00) / 100:,.2f}",
    "fee": lambda rng, cur: f"{cur}{rng.randint(15, 400)}.00",
    "rate": lambda rng, cur: f"{cur}{rng.randint(20, 900)}.00",
    "company": lambda rng, cur: rng.choice(COMPANIES),
    "person": lambda rng, cur: f"{rng.choice(FIRST)} {rng.choice(LAST)}",
    "address": lambda rng, cur: f"{rng.randint(2, 180)} {rng.choice(STREETS)}, {rng.choice(CITIES)}",
    "period": lambda rng, cur: rng.choice(["14 days", "30 days", "45 days", "60 days", "90 days", "one month",
                                           "two months", "three months", "six months"]),
    "terms": lambda rng, cur: rng.choice(["Net 15", "Net 30", "Net 45", "Net 60", "2/10 Net 30", "due on receipt"]),
    "id": lambda rng, cur: f"{rng.choice(['A', 'K', 'R', 'T'])}-{rng.randrange(100_000):05d}",
}
WINDOWED = {"rate", "period"}  # kinds whose values may hold over dated windows

# family -> (amendment term, keys {key: (noun, kind, labels)}, filler lines)
FAMILIES = {
    "invoice": ("Correction", {
        "invoice_number": ("invoice number", "id", ["Invoice number", "Invoice No."]),
        "previous_invoice": ("previous invoice number", "id", ["Previous invoice"]),
        "total_due": ("total due", "money", ["Total due", "Amount payable", "Balance due"]),
        "subtotal": ("subtotal before VAT", "money", ["Subtotal (excl. VAT)"]),
        "due_date": ("payment due date", "date", ["Due date", "Payment due"]),
        "invoice_date": ("invoice date", "date", ["Invoice date", "Date of issue"]),
        "vendor": ("vendor", "company", ["Vendor", "Supplier", "Issued by"]),
        "customer": ("customer", "company", ["Customer", "Bill to"]),
        "billing_address": ("billing address", "address", ["Billing address", "Invoice address"]),
        "shipping_address": ("shipping address", "address", ["Shipping address", "Deliver to"]),
        "payment_terms": ("payment terms", "terms", ["Payment terms", "Terms"]),
        "repeat_terms": ("payment terms for repeat orders", "terms", ["Terms for repeat orders"]),
        "hourly_rate": ("hourly consulting rate", "rate", ["Consulting rate", "Hourly rate"]),
        "travel_rate": ("hourly travel rate", "rate", ["Travel time rate"]),
    }, ["Thank you for your business.", "Please quote the invoice number with your payment.",
        "Goods remain our property until paid in full.", "Bank transfer only; no cheques."]),
    "purchase_order": ("Change", {
        "po_number": ("purchase order number", "id", ["PO number", "Purchase order no."]),
        "replaced_po": ("number of the order it replaces", "id", ["Replaces PO"]),
        "requester": ("requester", "person", ["Requested by", "Requester"]),
        "approver": ("approver", "person", ["Approved by"]),
        "delivery_date": ("required delivery date", "date", ["Required delivery date", "Deliver by"]),
        "order_date": ("order date", "date", ["Order date"]),
        "ship_to": ("delivery address", "address", ["Ship to", "Delivery address"]),
        "bill_to": ("invoicing address", "address", ["Bill to"]),
        "supplier": ("supplier", "company", ["Supplier", "Vendor"]),
        "carrier": ("carrier", "company", ["Carrier"]),
        "unit_price": ("unit price", "rate", ["Unit price"]),
        "freight": ("freight charge", "rate", ["Freight charge"]),
    }, ["Partial deliveries accepted.", "Attach the delivery note to the invoice.", "Goods inspected on receipt."]),
    "service_contract": ("Amendment", {
        "client": ("client", "company", ["Client", "Customer party"]),
        "provider": ("service provider", "company", ["Service provider", "Provider"]),
        "subcontractor": ("subcontractor", "company", ["Subcontractor"]),
        "start_date": ("commencement date", "date", ["Commencement date", "Start of services"]),
        "signature_date": ("date of signature", "date", ["Date of signature"]),
        "notice_period": ("termination notice period", "period", ["Termination notice", "Notice period"]),
        "price_notice": ("notice period for price changes", "period", ["Notice of price changes"]),
        "monthly_fee": ("monthly fee", "rate", ["Monthly fee", "Monthly charge"]),
        "setup_fee": ("one-off setup fee", "money", ["Setup fee"]),
        "late_fee": ("late payment fee", "fee", ["Late payment fee"]),
        "callout_fee": ("emergency call-out fee", "fee", ["Emergency call-out fee"]),
    }, ["The Provider performs the services with reasonable skill and care.",
        "Neither party may assign this agreement without written consent.",
        "Confidential information is not disclosed to third parties."]),
    "insurance_policy": ("Endorsement", {
        "policy_number": ("policy number", "id", ["Policy number", "Policy no."]),
        "previous_policy": ("previous policy number", "id", ["Previous policy"]),
        "policyholder": ("policyholder", "person", ["Policyholder", "Insured"]),
        "beneficiary": ("beneficiary", "person", ["Beneficiary"]),
        "insurer": ("insurer", "company", ["Insurer", "Underwriter"]),
        "broker": ("broker", "company", ["Broker"]),
        "premium": ("monthly premium", "rate", ["Monthly premium", "Premium per month"]),
        "sum_insured": ("sum insured", "money", ["Sum insured"]),
        "deductible": ("deductible per claim", "fee", ["Deductible", "Excess per claim"]),
        "admin_fee": ("fee for policy changes", "rate", ["Administration fee"]),
        "cancellation_notice": ("notice to cancel", "period", ["Cancellation notice"]),
        "claim_window": ("time limit to report a claim", "period", ["Claims to be reported within"]),
    }, ["Claims must be supported by receipts.", "Cover is subject to the general conditions.",
        "Premiums are collected by direct debit."]),
}
NEAR = {"previous_invoice": "invoice_number", "subtotal": "total_due", "invoice_date": "due_date",
        "customer": "vendor", "shipping_address": "billing_address", "repeat_terms": "payment_terms",
        "travel_rate": "hourly_rate", "replaced_po": "po_number", "approver": "requester",
        "order_date": "delivery_date", "bill_to": "ship_to", "carrier": "supplier", "freight": "unit_price",
        "subcontractor": "provider", "signature_date": "start_date", "price_notice": "notice_period",
        "setup_fee": "monthly_fee", "callout_fee": "late_fee", "previous_policy": "policy_number",
        "beneficiary": "policyholder", "broker": "insurer", "sum_insured": "premium", "admin_fee": "deductible",
        "claim_window": "cancellation_notice"}
END = date(2099, 12, 31)


def _fmt(d):
    return f"{d.day} {MONTHS[d.month - 1]} {d.year}"


def resolve(facts, key, loc, day, seen=()):
    """The fact giving `key` on `day` at `loc`: the highest-ranked live fact there, references followed."""
    live = [f for f in facts if f["key"] == key and f["loc"] == loc and f["start"] <= day <= f["end"]]
    if not live or loc in seen:
        return None
    best = max(live, key=lambda f: f["rank"])
    return resolve(facts, key, best["ref"], day, seen + (loc,)) if best["ref"] else best


@dataclass
class BusinessDocumentExtractionConfig(Config):
    fields: float = 2.0
    near: float = 0.3
    missing: float = 0.12
    windows: float = 0.1
    periods: float = 2.0
    amendments: float = 0.5
    stack: float = 0.0
    refs: float = 0.1
    chain: float = 1.0
    unordered: float = 0.0
    filler: float = 1.0

    def apply_difficulty(self, level):
        self.fields = 2 + 1.2 * level
        self.near = min(0.9, 0.3 + 0.15 * level)
        self.missing = 0.12 + 0.02 * level
        self.windows = min(0.5, 0.1 + 0.1 * level)
        self.periods = 2 + 0.5 * level
        self.amendments = 0.5 + 1.0 * level
        self.stack = min(0.6, 0.15 * level)
        self.refs = min(0.5, 0.1 + 0.1 * level)
        self.chain = 1 + 0.4 * level
        self.unordered = min(0.6, 0.15 * level)
        self.filler = 1 + 0.5 * level


class BusinessDocumentExtraction(Task):
    summary = ("Find the value in force on a date in an invoice, purchase order, contract or insurance policy: "
               "numbered amendments override printed values and each other from their effective dates, schedule "
               "references chain, values vary over dated windows, and near-miss keys sit alongside.")
    task_version = 2

    def __init__(self, config=None):
        super().__init__(config=config or BusinessDocumentExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        family = rng.choice(sorted(FAMILIES))
        term, keys, filler = FAMILIES[family]
        cur, start = rng.choice(["€", "$", "£"]), date(2025, rng.randint(1, 12), 1)
        used, facts, letters = set(), [], iter("ABCDEFGH")

        def fresh(key):  # values are distinct, so a span names one fact; None once the kind's values run out
            values = (GEN[keys[key][1]](rng, cur) for _ in range(30))
            return next((v for v in values if v not in used), None)

        def fact(key, loc, rank=0, a=start, b=END, ref=None, value=None):
            used.add(value)
            facts.append({"key": key, "loc": loc, "rank": rank, "start": a, "end": b, "ref": ref, "value": value,
                          "mark": f"f{len(facts)}"})

        def place(key, loc, depth):  # a printed value, dated windows, or a reference to a new schedule
            if depth and rng.random() < c.refs and (target := next(letters, None)):
                fact(key, loc, ref=target)
                if not place(key, target, depth - 1):
                    facts.pop()  # no dangling reference
                    return False
                return True
            if keys[key][1] in WINDOWED and rng.random() < c.windows:
                a, placed = start, False
                for _ in range(max(2, sround(c.periods, seed=rng.random()))):
                    b = a + timedelta(days=rng.randint(60, 240))
                    if (value := fresh(key)) is not None:
                        fact(key, loc, a=a, b=b, value=value)
                        placed = True
                    a = b + timedelta(days=1)
                return placed
            if (value := fresh(key)) is None:
                return False
            fact(key, loc, value=value)
            return True

        main = [k for k in keys if k not in NEAR]
        asked = rng.sample(main, min(len(main), 7, max(2, sround(c.fields, seed=rng.random()))))
        for key in main:  # an asked key may be missing (only its near miss stated); others appear at random
            if (key in asked and rng.random() >= c.missing) or (key not in asked and rng.random() < 0.5):
                place(key, "body", sround(c.chain, seed=rng.random()))
        for near, key in NEAR.items():
            if near in keys and key in asked and (rng.random() < c.near or not any(f["key"] == key for f in facts)):
                place(near, rng.choice(sorted({f["loc"] for f in facts if f["key"] == key} | {"body"})), 0)
        key = None
        rank = 0
        for _ in range(sround(c.amendments, seed=rng.random())):  # numbered amendments, maybe stacking
            if key is None or rng.random() >= c.stack:
                key = rng.choice(asked + [n for n in NEAR if n in keys and NEAR[n] in asked])
            a = start + timedelta(days=rng.randrange(600))
            b = a + timedelta(days=rng.randint(60, 300)) if keys[key][1] in WINDOWED and rng.random() < 0.4 else END
            loc = rng.choice(sorted({f["loc"] for f in facts if f["key"] == key} | {"body"}))
            if (value := fresh(key)) is None:
                continue
            target = next(letters, None) if rng.random() < c.refs / 2 else None
            rank += 1
            if target:  # the amendment points to a new schedule holding the value
                fact(key, loc, rank, a, b, ref=target)
                fact(key, target, value=value)
            else:
                fact(key, loc, rank, a, b, value=value)

        fields, gold = [], {}
        for key in asked:  # the query date falls near a date where the answer changes, or anywhere in the term
            edges = [f[e] for f in facts if f["key"] == key for e in ("start", "end") if f[e] != END]
            day = (rng.choice(edges) + timedelta(days=rng.choice([-1, 0, 1, rng.randint(-40, 40)]))
                   if edges and rng.random() < 0.7 else start + timedelta(days=rng.randrange(700)))
            hit = resolve(facts, key, "body", max(day, start))
            fields.append({"name": key, "type": "text",
                           "instruction": f"The {keys[key][0]} in force on {_fmt(max(day, start))}; null if none is."})
            gold[key] = hit["mark"] if hit else None

        # no printed start date: it would read as the answer to a commencement date the document leaves out
        doc = Doc().add(f"{family.replace('_', ' ').upper()}\nOrder of precedence: a "
                        f"numbered {term.lower()} prevails over the printed text and over any {term.lower()} with a "
                        "lower number, from its effective date until its end date if it has one; dated ranges are "
                        "inclusive. \"See Schedule X\" means the value stated in Schedule X.\n\n")

        def write(loc):  # the printed facts of a location, one line or one list of windows per key
            groups = {}
            for f in facts:
                if f["loc"] == loc and not f["rank"]:
                    groups.setdefault(f["key"], []).append(f)
            lines = list(groups.values())
            if loc == "body":
                lines += rng.sample(filler, min(len(filler), sround(c.filler, seed=rng.random())))
                rng.shuffle(lines)
            for group in lines:
                if isinstance(group, str):
                    doc.add(group + "\n")
                    continue
                label = rng.choice(keys[group[0]["key"]][2])
                if group[0]["end"] == END:
                    doc.add(f"{label}: " + (f"see Schedule {group[0]['ref']}." if group[0]["ref"] else "{v}") + "\n",
                            v=(group[0]["value"] or "", group[0]["mark"]))
                else:
                    doc.add(f"{label}:\n")
                    for f in group:
                        doc.add(f"  - {_fmt(f['start'])} to {_fmt(f['end'])}: {{v}}\n", v=(f["value"], f["mark"]))

        write("body")
        for letter in sorted({f["loc"] for f in facts} - {"body"}):
            doc.add(f"\nSchedule {letter}\n")
            write(letter)
        amendments = sorted((f for f in facts if f["rank"]), key=lambda f: f["rank"])
        if amendments:
            doc.add(f"\n{term}s\n")
            if rng.random() < c.unordered:
                rng.shuffle(amendments)
        for f in amendments:
            where = "" if f["loc"] == "body" else f" in Schedule {f['loc']}"
            when = f"effective {_fmt(f['start'])}" + (f" until {_fmt(f['end'])}" if f["end"] != END else "")
            what = f"is as set out in Schedule {f['ref']}" if f["ref"] else "is {v}"
            doc.add(f"{term} No. {f['rank']} ({when}): the {keys[f['key']][0]}{where} {what}.\n",
                    v=(f["value"] or "", f["mark"]))
        spans = {k: doc.marks.get(m, []) if m else [] for k, m in gold.items()}
        rng.shuffle(fields)
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, family=family)
