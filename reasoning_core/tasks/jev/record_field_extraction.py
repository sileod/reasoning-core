"""Fill a person's record from a text about several people with near-miss names.

Each field holds the person's current value or null. Confusers state other values without asserting them: a
negation, a former or hoped-for value, or a relative's value; null fields often have one, so null means
"not stated" rather than "not mentioned". Levels add people (who share a first name or surname with the person),
confusers, fields, short references (a first name or surname, once it is unambiguous), chains of "same as"
statements, whose answer is another person's value, and names that are also field values (May, Sydney, Paris).
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, Task, stochastic_rounding as sround
from reasoning_core.tasks.jev._extraction import CITIES, COMPANIES, FIRST, LAST, MONTHS, Doc, article, \
    extraction_entry

ROLES = ["data engineer", "nurse", "accountant", "site manager", "translator", "pilot", "chemist",
         "sales director", "architect", "paralegal", "electrician", "editor"]
# Names that are also values of the fields (months, cities): a person named May born in May, a Ms. Sydney living in
# Sydney. Type-based guessing ("the span that looks like a city") then fails; the role in the sentence decides.
COLLIDING_FIRST = ["May", "June", "April", "Florence", "Sydney", "Victoria", "Austin", "Paris", "Georgia", "Adelaide"]
COLLIDING_LAST = ["London", "Paris", "Florence", "Sydney", "Austin", "Lima", "Porto", "Perth", "Darwin", "Victoria"]
RECORD_CITIES = CITIES + ["Florence", "Sydney", "Victoria", "Austin", "Paris", "London", "Adelaide"]
RELATIVES = ["brother", "sister", "manager", "neighbor", "cousin", "former partner"]
DOMAINS = ["mailbox.org", "fastmail.com", "proton.me", "posteo.net"]
SAME = {"city": "{w} lives in the same city as {x}.", "employer": "{w} works at the same company as {x}.",
        "job_title": "{w} has the same job as {x}.", "phone": "{w} shares a phone line with {x}.",
        "birth_date": "{w} was born on the same day as {x}, a twin."}


def _phone(rng, person):
    return f"+{rng.choice([33, 44, 49, 351])} {rng.randint(600, 799)} {rng.randint(100, 999)} {rng.randint(1000, 9999)}"


def _email(rng, person):
    first, last = person
    return rng.choice([f"{first}.{last}", f"{first[0]}.{last}", f"{first}{last[0]}", f"{last}.{first}"]).lower() \
        + "@" + rng.choice(DOMAINS)


# field -> (instruction, value(rng, person), assertions, confusers, relative's value); {a} is the value's article
ATTRS = {
    "city": ("The city where {w} currently lives.", lambda rng, p: rng.choice(RECORD_CITIES),
             ["{w} lives in {v}.", "{w} is based in {v}.", "These days {w} lives in {v}."],
             ["{w} does not live in {v}.", "{w} lived in {v} as a student and has since moved away.",
              "{w} is thinking about moving to {v}.", "{w} spent a holiday in {v}."],
             "{w}'s {r} lives in {v}."),
    "employer": ("The company {w} currently works for.", lambda rng, p: rng.choice(COMPANIES),
                 ["{w} works for {v}.", "{w} is employed by {v}.", "{w} joined {v} two years ago and is still there."],
                 ["{w} left {v} in 2019.", "{w} turned down a job offer from {v}.",
                  "{w} has a job interview at {v} next week.", "{w} never worked for {v}."],
                 "{w}'s {r} works for {v}."),
    "job_title": ("The job title of {w}.", lambda rng, p: rng.choice(ROLES),
                  ["{w} works as {a} {v}.", "{w} is {a} {v} by profession."],
                  ["{w} trained as {a} {v} but never worked as one.", "{w} hopes to become {a} {v}.",
                   "{w} is not {a} {v}, whatever the badge says."],
                  "{w}'s {r} is {a} {v}."),
    "phone": ("The phone number of {w}.", _phone,
              ["{w}'s phone number is {v}.", "{w} can be reached at {v}."],
              ["The number {v} no longer belongs to {w}.", "{w} stopped using the old number {v}."],
              "{w}'s {r} can be reached at {v}."),
    "email": ("The email address of {w}.", _email,
              ["{w}'s email address is {v}.", "{w} reads mail at {v}."],
              ["{w} closed the account {v} last spring.", "The address {v} is not {w}'s, despite the name."],
              "Mail for {w}'s {r} goes to {v}."),
    "birth_date": ("The date of birth of {w}.",
                   lambda rng, p: f"{rng.randint(1, 28)} {rng.choice(MONTHS)} {rng.randint(1958, 2004)}",
                   ["{w} was born on {v}.", "{w}'s date of birth is {v}."],
                   ["{w} got married on {v}.", "{w} moved house on {v}.", "{w} was not born on {v}, as an old file claims."],
                   "{w}'s {r} was born on {v}."),
}


def _people(rng, n, p_near, p_collide):
    """The person, then n others; with probability p_near another shares the person's first name or surname, and
    each name is one that is also a field value (a month, a city) with probability p_collide."""
    def name(pool, colliding):
        return rng.choice(colliding if rng.random() < p_collide else pool)

    target = (name(FIRST, COLLIDING_FIRST), name(LAST, COLLIDING_LAST))
    people = [target]
    while len(people) < n + 1:
        near = rng.random() < p_near
        first = target[0] if near and rng.random() < 0.5 else name(FIRST, COLLIDING_FIRST)
        last = target[1] if near and first != target[0] else name(LAST, COLLIDING_LAST)
        if (first, last) not in people:
            people.append((first, last))
    return people


@dataclass
class RecordFieldExtractionConfig(Config):
    others: float = 0.5
    near_name: float = 0.0
    confusers: float = 0.0
    fields: float = 2.5
    short_refs: float = 0.0
    hops: float = 0.0
    chain: float = 1.0
    collide: float = 0.0

    def apply_difficulty(self, level):
        self.others = 0.5 + 1.3 * level
        self.near_name = min(0.9, 0.25 * level)
        self.confusers = 0.8 * level
        self.fields = 2.5 + 0.6 * level
        self.short_refs = min(0.8, 0.2 * level)
        self.hops = min(0.7, 0.2 * level)
        self.chain = 1 + 0.4 * level
        self.collide = min(0.6, 0.15 * level)


class RecordFieldExtraction(Task):
    summary = ("Fill a person's city, employer, job title, phone, email and birth-date fields, or null, from prose "
               "about several near-miss-named people with negated, former, hoped-for and relatives' values and "
               "'same city/company/job as' chains through other people, and names that are also months or cities.")
    task_version = 2

    def __init__(self, config=None):
        super().__init__(config=config or RecordFieldExtractionConfig())

    def generate_entry(self, state_seed=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, c = random.Random(state_seed), self.config
        people = _people(rng, sround(c.others, seed=rng.random()), c.near_name, c.collide)
        target = people[0]
        names = rng.sample(sorted(ATTRS), min(len(ATTRS), max(2, sround(c.fields, seed=rng.random()))))
        stated = [n for n in names if rng.random() < 0.7] or names[:1]
        values = {n: ATTRS[n][1](rng, target) for n in stated}

        statements, fixed = [], set()  # (person index, template, value, mark, other person index)
        for n in stated:  # the value, or a chain "same as" other people ending at the value
            holder, others = 0, list(range(1, len(people)))
            if n in SAME and others and rng.random() < c.hops:
                for j in rng.sample(others, min(len(others), max(1, sround(c.chain, seed=rng.random())))):
                    statements.append((holder, SAME[n], None, None, j))
                    fixed.add((j, n))
                    holder = j
            fixed.add((holder, n))
            statements.append((holder, rng.choice(ATTRS[n][2]), values[n], n, None))
        for i, person in enumerate(people[1:], 1):
            for n in rng.sample(names, rng.randint(1, min(3, len(names)))):
                if (i, n) not in fixed:
                    statements.append((i, rng.choice(ATTRS[n][2]), ATTRS[n][1](rng, person), None, None))
        for _ in range(sround(c.confusers, seed=rng.random())):  # mostly on null fields: null must be earned
            nulls = [n for n in names if n not in stated]
            n = rng.choice(nulls if nulls and rng.random() < 0.6 else names)
            value = ATTRS[n][1](rng, target)
            if value == values.get(n):
                continue
            relative = rng.random() < 0.3
            template = ATTRS[n][4] if relative else rng.choice(ATTRS[n][3])
            statements.append((0, template.replace("{r}", rng.choice(RELATIVES)), value, None, None))
        rng.shuffle(statements)

        full = [f"{f} {l}" for f, l in people]
        short = {i: [s for s in p if sum(s in q for q in people) == 1] for i, p in enumerate(people)}
        seen, doc = set(), Doc()
        def ref(i):
            name = full[i] if i not in seen or not short[i] or rng.random() >= c.short_refs else rng.choice(short[i])
            seen.add(i)
            return name

        for i, template, value, mark, j in statements:
            doc.add(template + " ", w=ref(i), x=ref(j) if j is not None else "", v=(value or "", mark),
                    a=article(value or "a"))
        fields = [{"name": n, "type": "text", "instruction": ATTRS[n][0].format(w=full[0])} for n in names]
        return extraction_entry(doc.text.strip(), fields, {n: doc.marks.get(n, []) for n in names}, state_seed)
