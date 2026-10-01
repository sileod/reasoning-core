"""Check a question's presupposition against derived facts, then answer from the facts.

Reworked from the generated presupposition_repair (ext #4 on v8_tiny). That version always asked
about the two alphabetically first locations, summed meters with coins, and "repaired" a false
premise by subtracting 3. Here counts are partly stated and partly derived through chains of
relations ("Bo has 4 more than Ann", "Cy has twice as many as Bo"), the question rests on a
premise that is false half the time -- a wrong count, or a wrong comparison -- and the answer
is the premise's status plus the value computed from the facts, so a reader who takes the
premise at face value gets the value wrong whenever it is false.
"""
import random
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, edict, stochastic_rounding as sround

NAMES = ["Ana", "Ben", "Cleo", "Dev", "Eli", "Fay", "Gus", "Hana", "Ivo", "Jun", "Kai", "Lea"]
ITEMS = ["coins", "stamps", "marbles", "shells", "cards", "books"]


@dataclass
class PremiseRepairConfig(Config):
    n_people: int = 3
    derived: int = 1
    max_value: int = 20

    def apply_difficulty(self, level):
        self.n_people = 3 + sround(0.8 * level)
        self.derived = 1 + sround(0.7 * level)
        self.max_value = 20 + 5 * level


def _relation(base, value, item):
    """A phrase stating value relative to base."""
    options = []
    if value > base:
        options.append(f"{value - base} more {item} than")
    if value < base:
        options.append(f"{base - value} fewer {item} than")
    if value == 2 * base:
        options.append(f"twice as many {item} as")
    if value * 2 == base:
        options.append(f"half as many {item} as")
    if value == base:
        options.append(f"as many {item} as")
    return random.choice(options)


class PremiseRepair(DevTask):
    summary = ("People hold counts that are stated or derived through chains of relations; a question "
               "rests on a premise (a stated count or a comparison) that is false half the time; report "
               "whether the premise holds and the answer computed from the facts.")
    config_cls = PremiseRepairConfig
    task_version = 1

    def generate_entry(self):
        cfg = self.config
        people = random.sample(NAMES, cfg.n_people)
        item = random.choice(ITEMS)
        value = {p: random.randint(2, cfg.max_value) for p in people}
        order = people[:]
        random.shuffle(order)
        facts, depth = [], {}
        # The first n - derived people are stated; each later one is related to an earlier one.
        n_stated = max(1, cfg.n_people - cfg.derived)
        for i, p in enumerate(order):
            if i < n_stated:
                facts.append(f"{p} has {value[p]} {item}.")
                depth[p] = 0
                continue
            ref = random.choice(order[:i])
            if random.random() < 0.25 and value[ref] <= cfg.max_value // 2:
                value[p] = 2 * value[ref]
            elif random.random() < 0.15 and value[ref] % 2 == 0:
                value[p] = value[ref] // 2
            facts.append(f"{p} has {_relation(value[ref], value[p], item)} {ref}.")
            depth[p] = depth[ref] + 1
        random.shuffle(facts)
        a, b = sorted(random.sample(people, 2), key=lambda p: -depth[p])
        truth = random.random() < 0.5
        kind = random.choice(["count", "compare"])
        if kind == "count":
            claimed = value[a] if truth else value[a] + random.choice([-3, -2, -1, 1, 2, 3, 5])
            if claimed < 0:
                return None
            premise = f"{a} has {claimed} {item}"
            question = random.choice([
                (f"Given that {a} has {claimed} {item}, how many {item} do {a} and {b} have together?",
                 value[a] + value[b], claimed + value[b]),
                (f"Since {a} has {claimed} {item}, how many more {item} does {a} have than {b}?",
                 value[a] - value[b], claimed - value[b]),
            ])
        else:
            if value[a] == value[b]:
                return None
            big, small = (a, b) if (value[a] > value[b]) == truth else (b, a)
            premise = f"{big} has more {item} than {small}"
            question = (f"Since {big} has more {item} than {small}, how many more {item} does {big} have "
                        f"than {small}?", value[big] - value[small], abs(value[big] - value[small]))
        text, answer, naive = question
        if not truth and answer == naive:
            return None
        meta = edict(facts=facts, question=text, premise=premise, premise_true=truth, naive=naive,
                     depth=depth[a])
        return Entry(metadata=meta, answer=f"{'true' if truth else 'false'}, {answer}")

    def render_prompt(self, m):
        facts = "\n".join(m.facts)
        return (f"Facts:\n{facts}\n\nQuestion: {m.question}\n\n"
                "The question takes a premise for granted. Check it against the facts. Then answer the "
                "question using the facts, not the premise (if the premise is false, the facts win; a "
                "difference can be negative).\n"
                "Answer as: true or false (whether the premise holds), a comma, then the number. "
                "Example: false, 7")

    def score_answer(self, answer, entry):
        got = [x.strip().lower().rstrip(".") for x in str(answer).split(",")]
        gold = entry.answer.split(", ")
        if len(got) != 2:
            return 0.0
        return float(got == gold)

    def balancing_key(self, problem):
        return problem.answer.split(",")[0]
