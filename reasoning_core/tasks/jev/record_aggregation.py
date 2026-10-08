"""Count, compare, and sum over an inventory; every answer is unique by construction.

Levels grow the inventory; from level 2 a compound count adds a quantity filter, and from level 3 a stock filter
as well. Ported from tasksource.jev.procedural.record_aggregation; its level tables stop at 4.
"""
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision, render_records
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

COLORS = ["red", "blue", "green", "black", "white", "gray", "orange", "purple", "yellow", "brown"]
OBJECTS = ["lamp", "chair", "kettle", "drill", "scarf", "clock", "vase", "rope", "tent", "mug"]
SIZES = [5, 12, 24, 40, 60]
CATEGORIES = ["tools", "kitchen", "garden", "office", "outdoor"]
COUNTS = [str(i) for i in range(9)] + ["9 or more"]  # Jev scores have at most 10 levels


@dataclass
class RecordAggregationConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class RecordAggregation(Task):
    summary = "Count, compare and sum over an inventory table, asked as typed decisions over one shared state."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or RecordAggregationConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        n = max(3, sround(SIZES[level] * rng.uniform(0.8, 1.2), seed=rng.random()))
        names = rng.sample([f"{c} {o}" for c in COLORS for o in OBJECTS], n)
        items = [{"item": name, "category": rng.choice(CATEGORIES), "quantity": rng.randint(1, 20),
                  "in_stock": rng.random() < 0.75} for name in names]

        sizes = {c: sum(i["category"] == c for i in items) for c in CATEGORIES}
        nonempty = [c for c in CATEGORIES if 1 <= sizes[c] <= 20]
        category = rng.choice(nonempty if nonempty and rng.random() < 0.9 else
                              [c for c in CATEGORIES if sizes[c] <= 20])
        members = [i for i in items if i["category"] == category]
        count = len(members)
        if members:  # decide the stock answer first so it is balanced at every size
            out_of_stock = rng.random() < 0.5
            for i in members:
                i["in_stock"] = True
            if out_of_stock:
                for i in rng.sample(members, rng.randint(1, max(1, len(members) // 2))):
                    i["in_stock"] = False

        # Largest quantity within the category when it has several items, else overall;
        # the leader is bumped until strictly largest so the answer is unique.
        pool = members if len(members) >= 2 else items
        scope = f"{category} items" if pool is members else "items"
        leader = max(pool, key=lambda i: i["quantity"])
        runner_up = max((i["quantity"] for i in pool if i is not leader), default=0)
        leader["quantity"] = max(leader["quantity"], runner_up + 1)
        rivals = sorted((i["item"] for i in pool if i is not leader), key=lambda _: rng.random())
        extra = [i["item"] for i in items if i["item"] not in rivals and i is not leader]
        options = sorted([leader["item"], *(rivals + extra)[:5]], key=lambda _: rng.random())

        total = sum(i["quantity"] for i in members)
        threshold = max(0, total + rng.choice([-3, -2, -1, 0, 1, 2]))

        questions = {
            "count_in_category": Decision(min(count, len(COUNTS) - 1), type="score", criteria=COUNTS,
                instructions=rng.choice(["How many items are in the {c} category?", "Count the {c} items.",
                                         "How many listed items belong to {c}?"]).format(c=category)),
            "largest_quantity": Decision(leader["item"], criteria=dict.fromkeys(options), instructions=rng.choice([
                "Among the {s}, which has the largest quantity?",
                "Which of the {s} has the highest quantity?"]).format(s=scope)),
            "any_out_of_stock": Decision(any(not i["in_stock"] for i in members), type="noul",
                instructions=rng.choice(["Is any {c} item out of stock?",
                                         "Is at least one {c} item not in stock?"]).format(c=category)),
            "total_above": Decision(total > threshold, type="noul", instructions=rng.choice([
                "Is the total quantity of {c} items greater than {t}?",
                "Do the {c} items add up to more than {t} units?"]).format(c=category, t=threshold)),
        }
        if level >= 2:
            cut = rng.randint(5, 15)
            stock = level >= 3
            hits = sum(i["category"] == category and i["quantity"] >= cut and (i["in_stock"] or not stock)
                       for i in items)
            questions["count_filtered"] = Decision(min(hits, len(COUNTS) - 1), type="score", criteria=COUNTS,
                instructions=rng.choice(["How many {c} items{s} have a quantity of at least {q}?",
                                         "Count the {c} items{s} whose quantity is {q} or more."]).format(
                    c=category, q=cut, s=" that are in stock" if stock else ""))
        state = render_records(items, rng.choice(["json", "table", "csv", "lines"]))
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])
