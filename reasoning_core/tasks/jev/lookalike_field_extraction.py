"""Fill the asked fields of a record from its rendered document, null when the asked role is not stated although
values of the same type with other roles are.

Latent structure: a record of typed roles (dates, amounts, people, identifiers, addresses, phone numbers, weights,
durations), each type with several roles (issue, delivery and expiry dates; subtotal, tax and deposit). A document
states a few roles per type with distinct values. Asked roles are stated ones or, at the missing rate, unstated
roles of a stated type, so every null has look-alikes: a value of its type under another role. An unstated role may
still appear with a placeholder (pending, N/A), which is null too. The renderer writes the stated roles as a form,
sectioned key-value blocks, a table, prose, an email, log lines or YAML-like keys, labels drawn from each role's
synonyms, dates and amounts in mixed conventions, and asks fields with a noun of the role, never saying the answer
may be absent (a cue is added on a random share of fields, whatever the answer). Levels add types, look-alikes per
type, asked fields, missing roles, placeholders, label paraphrases between question and document, and filler.
"""
import random
import string
from dataclasses import dataclass
from datetime import date, timedelta
from fractions import Fraction

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core import surface_forms as sf
from reasoning_core.tasks.jev._extraction import CITIES, FIRST, LAST, Doc, extraction_entry

# type: {role: (nouns for questions and prose, labels for forms)}. Roles of a type never share a noun or label, and
# none is a whole-word part of another, so an unstated role cannot be read off another role's line.
ROLES = {
    "date": {
        "issue_date": (["issue date", "date of issue"], ["Issue date", "Date issued", "Issued on"]),
        "order_date": (["order date", "date of the order"], ["Order date", "Ordered on"]),
        "ship_date": (["shipping date", "dispatch date"], ["Ship date", "Dispatched on", "Shipped on"]),
        "delivery_date": (["delivery date", "date of delivery"], ["Delivery date", "Delivered on"]),
        "due_date": (["due date", "payment deadline"], ["Due date", "Payment due by"]),
        "expiry_date": (["expiry date", "expiration date"], ["Expiry date", "Valid until", "Expires on"]),
        "start_date": (["start date", "commencement date"], ["Start date", "Starts on"]),
        "end_date": (["end date", "termination date"], ["End date", "Ends on"]),
        "signing_date": (["signing date", "signature date"], ["Date signed", "Signed on"]),
        "renewal_date": (["renewal date"], ["Renewal date", "Renews on"]),
        "appointment_date": (["appointment date", "visit date"], ["Appointment date", "Scheduled visit"]),
    },
    "amount": {
        "subtotal": (["subtotal", "net amount"], ["Subtotal", "Net amount", "Amount before tax"]),
        "tax": (["tax amount", "VAT amount"], ["Tax", "VAT", "Sales tax"]),
        "total": (["total", "grand total"], ["Total", "Grand total", "Total amount"]),
        "deposit": (["deposit", "down payment"], ["Deposit", "Down payment", "Advance paid"]),
        "discount": (["discount", "rebate"], ["Discount", "Rebate"]),
        "shipping_cost": (["shipping cost", "delivery charge"], ["Shipping cost", "Delivery charge"]),
        "outstanding_balance": (["outstanding balance", "remaining balance"],
                                ["Outstanding balance", "Balance remaining"]),
        "refund": (["refund", "refunded amount"], ["Refund", "Amount refunded"]),
        "service_fee": (["service fee", "handling fee"], ["Service fee", "Handling fee"]),
        "salary": (["salary", "annual pay"], ["Salary", "Annual pay"]),
    },
    "person": {
        "sender": (["sender", "person who sent it"], ["Sender", "Sent by"]),
        "recipient": (["recipient", "addressee"], ["Recipient", "Addressee"]),
        "approver": (["approver", "person who approved it"], ["Approver", "Approved by"]),
        "contact_person": (["contact person", "point of contact"], ["Contact person", "Point of contact"]),
        "author": (["author", "person who wrote it"], ["Author", "Written by", "Prepared by"]),
        "reviewer": (["reviewer", "person who reviewed it"], ["Reviewer", "Reviewed by"]),
        "manager": (["manager", "supervisor"], ["Manager", "Supervisor"]),
        "signatory": (["signatory", "person who signed it"], ["Signatory", "Signature"]),
        "technician": (["technician", "engineer on site"], ["Technician", "Engineer on site"]),
        "driver": (["driver", "courier"], ["Driver", "Courier"]),
    },
    "id": {
        "order_number": (["order number", "order ID"], ["Order number", "Order no.", "Order ID"]),
        "tracking_number": (["tracking number", "tracking ID"], ["Tracking number", "Tracking no."]),
        "invoice_number": (["invoice number"], ["Invoice number", "Invoice no."]),
        "account_number": (["account number"], ["Account number", "Account no."]),
        "case_number": (["case number", "case ID"], ["Case number", "Case no."]),
        "booking_reference": (["booking reference", "confirmation code"], ["Booking reference", "Confirmation code"]),
        "customer_reference": (["customer reference"], ["Customer reference", "Your reference"]),
        "policy_number": (["policy number"], ["Policy number", "Policy no."]),
        "employee_id": (["employee ID", "staff number"], ["Employee ID", "Staff number"]),
        "serial_number": (["serial number"], ["Serial number", "Serial no."]),
    },
    "address": {
        "billing_address": (["billing address"], ["Billing address", "Bill to"]),
        "shipping_address": (["shipping address", "delivery address"], ["Shipping address", "Deliver to"]),
        "return_address": (["return address"], ["Return address", "Return to"]),
        "pickup_address": (["pickup address", "collection address"], ["Pickup address", "Collect from"]),
        "site_address": (["site address", "work location"], ["Site address", "Work location"]),
        "registered_office": (["registered office", "head office address"], ["Registered office", "Head office"]),
        "home_address": (["home address", "residential address"], ["Home address", "Residential address"]),
    },
    "phone": {
        "office_phone": (["office phone number", "office line"], ["Office phone", "Office line"]),
        "mobile_number": (["mobile number", "cell phone number"], ["Mobile", "Cell phone"]),
        "support_line": (["support line", "helpdesk number"], ["Support line", "Helpdesk"]),
        "fax_number": (["fax number"], ["Fax", "Fax number"]),
        "emergency_number": (["emergency number", "out-of-hours number"], ["Emergency number", "Out of hours"]),
    },
    "weight": {
        "gross_weight": (["gross weight"], ["Gross weight", "Weight incl. packaging"]),
        "net_weight": (["net weight"], ["Net weight", "Weight excl. packaging"]),
        "tare_weight": (["tare weight", "empty weight"], ["Tare weight", "Empty weight"]),
        "max_load": (["maximum load", "load capacity"], ["Maximum load", "Load capacity"]),
    },
    "duration": {
        "notice_period": (["notice period"], ["Notice period", "Notice required"]),
        "warranty_period": (["warranty period", "guarantee period"], ["Warranty", "Guarantee"]),
        "trial_period": (["trial period", "probation period"], ["Trial period", "Probation"]),
        "payment_terms": (["payment terms", "payment period"], ["Payment terms", "Pay within"]),
        "lead_time": (["lead time", "processing time"], ["Lead time", "Processing time"]),
    },
}
SECTIONS = {"date": "Dates", "amount": "Amounts", "person": "People", "id": "References", "address": "Addresses",
            "phone": "Contact", "weight": "Measurements", "duration": "Terms"}
TITLES = ["Record", "Summary", "Details", "Form", "Notice", "Confirmation", "Statement", "File", "Sheet", "Report"]
SUBJECTS = ["Account", "Client", "Case", "Job", "Transaction", "Request", "Customer", "Project", "Service", "Order"]
FILLER = ["This document was generated automatically.", "Please keep this for your records.",
          "Contact us with any questions.", "Thank you for your business.", "Page 1 of 1.",
          "Information is correct at the time of printing.", "Handle personal data in line with company policy.",
          "Changes must be confirmed in writing."]
PLACEHOLDERS = ["pending", "not yet assigned", "to be confirmed", "unknown", "N/A", "TBD", "-"]  # words first
QUESTIONS = ["The {n}.", "What is the {n}?", "Find the {n}.", "The {n} given in the document.", "Give the {n}."]
NULL_CUES = ["Null if not stated.", "Leave it empty if the document gives none.", "Answer null if there is none."]
LAYOUTS = ["form", "sections", "table", "wide_table", "prose", "email", "log", "yaml"]
CURRENCIES = ["$", "€", "£", " EUR", " USD", " CHF"]
STREETS = ["Harbour Road", "Elm Street", "Rue des Lilas", "Kings Avenue", "Mill Lane", "Via Roma", "Calle Mayor",
           "Station Road", "Birch Close", "Park Lane", "Quay Street", "Rosenweg"]


def _money(cents, cur, style):
    s = sf.NUMBER_STYLES[style]
    text = f"{sf.format_number(cents // 100, style)}{s.decimal}{cents % 100:02d}"
    return f"{cur}{text}" if not cur.startswith(" ") else f"{text}{cur}"


def _identifier(rng):
    d, u = string.digits, string.ascii_uppercase
    shape = rng.choice(["AA-ddddd", "dddddddd", "Adddddd", "AAAdddd", "dddd-dddd", "AA/dd/dddd"])
    return "".join(rng.choice(u) if ch == "A" else rng.choice(d) if ch == "d" else ch for ch in shape)


@dataclass
class LookalikeFieldExtractionConfig(Config):
    types: float = 2.0
    lookalikes: float = 2.0
    fields: float = 2.0
    missing: float = 0.15
    placeholder: float = 0.05
    paraphrase: float = 0.3
    date_variety: float = 0.2
    number_style: float = 0.0
    filler: float = 1.0
    null_cue: float = 0.1

    def apply_difficulty(self, level):
        self.types = 2 + 0.75 * level
        self.lookalikes = 2 + 0.5 * level
        self.fields = 2 + 1.0 * level
        self.missing = 0.15 + 0.0375 * level
        self.placeholder = min(0.3, 0.05 + 0.06 * level)
        self.paraphrase = min(0.8, 0.3 + 0.12 * level)
        self.date_variety = min(0.8, 0.2 + 0.15 * level)
        self.number_style = min(0.4, 0.1 * level)
        self.filler = 1 + 0.75 * level


class LookalikeFieldExtraction(Task):
    summary = ("Fill asked fields (dates, amounts, people, ids, addresses, phones, weights, durations by role) from "
               "a form, sections, table, prose, email, log or YAML-like record; an asked role that is not stated is "
               "null although other roles of its type are (issue date beside delivery date, subtotal beside tax) or "
               "it shows a placeholder, and questions never say the answer may be absent.")
    task_version = 2

    def __init__(self, config=None):
        super().__init__(config=config or LookalikeFieldExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        types = rng.sample(sorted(ROLES), min(len(ROLES), max(1, sround(c.types, seed=rng.random()))))
        stated, unstated = {}, {}
        for t in types:
            roles = sorted(ROLES[t])
            rng.shuffle(roles)
            k = min(len(roles) - 1, max(1, sround(c.lookalikes, seed=rng.random())))
            stated[t], unstated[t] = roles[:k], roles[k:]

        # Asked roles: a stated one, or at the missing rate an unstated role of a stated type (its look-alikes stay).
        asked, gold = [], {}
        for _ in range(max(1, sround(c.fields, seed=rng.random()))):
            t = rng.choice(types)
            absent = rng.random() < c.missing
            pool = [r for r in (unstated[t] if absent else stated[t]) if r not in gold]
            if not pool:
                continue
            role = rng.choice(pool)
            asked.append((t, role))
            gold[role] = None if absent else role
        placeholders = {role for t, role in asked if gold[role] is None and rng.random() < c.placeholder}

        # Values: distinct across the document, so a span names one role.
        numbers = rng.choice(["eu", "si", "swiss"]) if rng.random() < c.number_style else "en"
        cur = rng.choice(CURRENCIES)
        main_format = rng.choice(["iso"] + sf.UNAMBIGUOUS_DATES)
        start = date(2018, 1, 1) + timedelta(days=rng.randrange(3000))
        used = set()

        def value(t):
            for _ in range(50):
                if t == "date":
                    fmt = rng.choice(sf.UNAMBIGUOUS_DATES + ["iso"]) if rng.random() < c.date_variety else main_format
                    v = sf.render_date(start + timedelta(days=rng.randrange(-200, 400)), fmt)
                elif t == "amount":
                    v = _money(rng.randrange(500, 900_000), cur, numbers)
                elif t == "person":
                    v = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
                elif t == "id":
                    v = _identifier(rng)
                elif t == "address":
                    v = f"{rng.randint(2, 240)} {rng.choice(STREETS)}, {rng.choice(CITIES)}"
                elif t == "phone":
                    v = "+{} {} {} {}".format(rng.randint(1, 99), rng.randint(100, 999), rng.randint(100, 999),
                                              rng.randint(1000, 9999))
                elif t == "weight":
                    n, unit = rng.choice([(Fraction(rng.randint(2, 9000), 10), "kg"), (rng.randint(50, 20_000), "g"),
                                          (rng.randint(2, 900), "lb")])
                    v = f"{sf.format_number(n, numbers, 1)} {unit}"
                else:
                    n, unit = rng.choice([(rng.randint(2, 30), "days"), (rng.randint(2, 12), "weeks"),
                                          (rng.randint(2, 24), "months")])
                    v = f"{sf.words(n) if rng.random() < 0.3 else n} {unit}"
                if v and v not in used:
                    used.add(v)
                    return v
            raise RuntimeError(f"no fresh {t} value")

        lines = [(t, role, value(t)) for t in types for role in stated[t]]
        lines += [(t, role, None) for t, role in asked if role in placeholders]
        rng.shuffle(lines)

        layout, doc = rng.choice(LAYOUTS), Doc()
        title = f"{rng.choice(SUBJECTS)} {rng.choice(TITLES).lower()}"
        notes = rng.sample(FILLER, min(len(FILLER), sround(c.filler, seed=rng.random())))
        amounts = numbers != "en" and any(t == "amount" and v for t, _, v in lines)
        header = title + (f" ({sf.NUMBER_STYLES[numbers].convention})" if amounts else "")
        prose = layout in ("prose", "email", "log")
        nouns = {role: rng.choice(ROLES[t][role][0]) for t, role, _ in lines}

        def slot(role, v):  # stated values are marked; a placeholder is plain text
            return (v, role) if v else rng.choice(PLACEHOLDERS[:4] if prose else PLACEHOLDERS)

        def label(t, role):
            return rng.choice(ROLES[t][role][1])

        if layout in ("form", "sections", "yaml"):
            doc.add(f"# {header}\n" if layout == "yaml" else f"{header}\n\n")
            groups = [(None, lines)] if layout == "form" else [(t, [x for x in lines if x[0] == t]) for t in types]
            for t, group in groups:
                if layout == "sections":
                    doc.add(f"{SECTIONS[t]}\n")
                elif layout == "yaml":
                    doc.add(f"{SECTIONS[t].lower()}:\n")
                for t2, role, v in group:
                    key = label(t2, role)
                    if layout == "yaml":
                        key = key.lower().replace(".", "").replace(" ", "_")
                    doc.add(("  " if layout != "form" else "") + key + ": {v}\n", v=slot(role, v))
                if layout == "sections":
                    doc.add("\n")
            if notes and layout != "yaml":
                doc.add(("" if layout == "sections" else "\n") + "\n".join(notes))
        elif layout == "table":
            doc.add(f"{header}\n\n| Field | Value |\n|---|---|\n")
            for t, role, v in lines:
                doc.add(f"| {label(t, role)} | {{v}} |\n", v=slot(role, v))
            doc.add("\n" + " ".join(notes))
        elif layout == "wide_table":
            doc.add(f"{header}\n\n| " + " | ".join(label(t, role) for t, role, _ in lines) + " |\n|"
                    + "---|" * len(lines) + "\n|")
            for t, role, v in lines:
                doc.add(" {v} |", v=slot(role, v))
            doc.add("\n\n" + " ".join(notes))
        elif layout in ("prose", "email"):
            doc.add(f"Subject: {header}\n\nHello,\n\nHere are the details we have on file. " if layout == "email"
                    else f"{header}. ")
            for t, role, v in lines:
                patterns = ["The {n} is {v}. ", "It lists {v} as the {n}. "]
                patterns += ["{v} is the {n}. "] if v and not v[0].islower() else []  # never a lowercase sentence start
                pattern = rng.choice(patterns) if v else patterns[0]
                doc.add(pattern.replace("{n}", nouns[role]), v=slot(role, v))
            doc.add(" ".join(notes))
            if layout == "email":
                doc.add(f"\n\nKind regards,\nThe {rng.choice(['operations', 'accounts', 'service', 'support'])} team")
        else:  # log lines
            for i, (t, role, v) in enumerate(lines):
                doc.add(f"{(start + timedelta(days=i // 3)).isoformat()} INFO {title.lower().replace(' ', '.')} set "
                        f"\"{nouns[role]}\" to {{v}}\n", v=slot(role, v))
            for note in notes:
                doc.add(f"{(start + timedelta(days=len(lines) // 3)).isoformat()} NOTE {note}\n")

        # Questions name the role by a noun; where the document words roles by nouns, another at the paraphrase rate.
        fields = []
        for t, role in asked:
            others = [n for n in ROLES[t][role][0] if n != nouns.get(role)]
            n = (rng.choice(others) if others and prose and rng.random() < c.paraphrase
                 else nouns.get(role) or rng.choice(ROLES[t][role][0]))
            instruction = rng.choice(QUESTIONS).format(n=n)
            if rng.random() < c.null_cue:
                instruction += " " + rng.choice(NULL_CUES)
            fields.append({"name": role, "type": "text", "instruction": instruction})
        spans = {role: doc.marks.get(role, []) if gold[role] else [] for _, role in asked}
        return extraction_entry(doc.text.strip(), fields, spans, state_seed, layout=layout, types=types)
