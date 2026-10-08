"""Exact arithmetic over an order, an account ledger, or a schedule.

Numeric answers are choices among the gold value and typical slips (a skipped line, a sign error, an hour carry,
a rule applied the wrong way). Graded probabilities (k out of n) are asked as whether the event is more likely
than not, with `soft` = k/n; they are left out when k/n is within 0.1 of 1/2. Ported from
tasksource.jev.procedural.arithmetic (renamed: the main roster has arithmetics); its level tables stop at 4.
"""
import json
import random
from dataclasses import dataclass

from reasoning_core.decision import Decision, render_records
from reasoning_core.template import Config, Entry, Task, stochastic_rounding as sround

OBJECTS = ["lamp", "chair", "kettle", "drill", "scarf", "clock", "vase", "rope", "tent", "mug"]
COUNTS = [str(i) for i in range(10)]  # Jev scores have at most 10 levels
CURRENCIES = ["$", "€", "£"]
TASK_NAMES = ["email triage", "code review", "standup", "design sync", "report writing",
              "client call", "inventory check", "backup check", "planning", "interviews"]
SPEND = ["At most half of the budget.", "More than half of the budget, but within it.", "Over the budget."]
DRIFT = ["Fell by more than 50.", "Changed by 50 or less.", "Rose by more than 50."]


def _numeric(rng, gold, slips, fmt, instructions, offsets=(1, 2, 5, 10, 20)):
    """Gold among four distinct wrong values, typical slips first, then near misses.

    Gold's rank among the five is uniform, so sorted options do not reveal it.
    """
    near = [gold + sign * o for o in offsets for sign in (-1, 1)]
    below, above = [], []
    for v in rng.sample(slips, len(slips)) + rng.sample(near, len(near)):
        if v >= 0 and v != gold and v not in below + above:
            (below if v < gold else above).append(v)
    rank = rng.choice([r for r in range(5) if r <= len(below) and 4 - r <= len(above)])
    values = sorted(below[:rank] + [gold] + above[:4 - rank])
    if rng.random() < 0.5:
        values = rng.sample(values, len(values))
    return Decision(fmt(gold), criteria=dict.fromkeys(map(fmt, values)), instructions=instructions)


def _likely(pool, qid, k, n, instructions):
    """A k-out-of-n event asked as more likely than not, unless k/n is too close to call."""
    if abs(k / n - 1 / 2) >= 1 / 10:
        pool[qid] = Decision(k / n > 1 / 2, type="noul", soft=round(k / n, 6), instructions=instructions)


def _near(rng, value, step):
    """A threshold just above or below ``value``, each half the time."""
    return value + rng.choice([-1, 1]) * step * rng.randint(1, 3)


def _order(rng, level):
    n = min(len(OBJECTS), sround(2 + level * 1.2 + rng.random(), seed=rng.random()))
    lines = [{"item": item, "unit_price": rng.randint(2, 20 + 15 * level), "quantity": rng.randint(1, 3 + level)}
             for item in rng.sample(OBJECTS, n)]
    cost = lambda line: line["unit_price"] * line["quantity"]
    top = max(lines, key=cost)
    while sum(cost(line) == cost(top) for line in lines) > 1:
        top["quantity"] += 1
    total = sum(map(cost, lines))
    threshold = max(20, 5 * round(_near(rng, total, 10) / 5))
    discount, shipping = 5 * rng.randint(1, min(4, threshold // 20)), rng.choice([4, 6, 8])
    due = total - discount if total >= threshold else total + shipping
    wrong_rule = total + shipping if total >= threshold else total - discount
    slips = [total, wrong_rule, due - cost(lines[-1]), due - cost(top) + top["unit_price"], due + 10, due - 10]

    sym = rng.choice(CURRENCIES)
    money = lambda v: f"{sym}{v}"
    rule = (f"Orders of {money(threshold)} or more get {money(discount)} off; "
            f"smaller orders pay {money(shipping)} shipping.")
    style = rng.choice(["json", "table", "csv", "lines", "prose"])
    if style == "prose":
        body = " ".join(rng.choice(["{q} x {i} at {p} each.", "{i}: {q} units at {p} per unit."]).format(
            q=l["quantity"], i=l["item"], p=money(l["unit_price"])) for l in lines)
        state = f"Order: {body}\nRule: {rule}"
    elif style == "json":
        state = json.dumps({"currency": sym, "lines": lines, "rule": rule}, ensure_ascii=False)
    else:
        state = f"Order lines (prices in {sym}):\n{render_records(lines, style)}\n\nRule: {rule}"

    amount_due = _numeric(rng, due, slips, money, rng.choice([
        "How much is due for this order after the rule?", "What is the final amount to pay?",
        "After applying the rule, what does the order cost?"]))
    budget = max(1, _near(rng, due, 5))
    line_cut = rng.choice(sorted({cost(l) for l in lines}))
    quantities = sorted({l["quantity"] for l in lines})
    units = rng.choice(quantities[1:] or quantities)  # the minimum would make it certain
    pool = {
        "amount_due": amount_due,
        "largest_line": Decision(top["item"], criteria=dict.fromkeys(l["item"] for l in lines), instructions=
            rng.choice(["Which line costs the most in total?", "Which item accounts for the largest share of the bill?"])),
        "lines_above": Decision(sum(cost(l) > line_cut for l in lines), type="score", criteria=COUNTS, instructions=
            rng.choice(["How many lines cost more than {c} in total?",
                        "Count the lines whose total exceeds {c}."]).format(c=money(line_cut))),
    }
    _likely(pool, "random_line_bulk", sum(l["quantity"] >= units for l in lines), n, rng.choice([
        "If one order line is picked uniformly at random, is its quantity more likely than not to be at least {u}?",
        "Is a randomly chosen line more likely than not to order {u} or more units?"]).format(u=units))
    if rng.random() < 0.5:
        pool["within_budget"] = Decision(due <= budget, type="noul", instructions=rng.choice([
            "Is the amount due at most {b}?", "Does the order fit within a budget of {b}?"]).format(b=money(budget)))
    else:
        budget = rng.choice([due * 2 + rng.randint(0, 5), due + rng.randint(1, 20), max(1, due - rng.randint(1, 20))])
        pool["budget_use"] = Decision(2 if due > budget else 0 if 2 * due <= budget else 1, type="score",
            criteria=SPEND, instructions=rng.choice([
                "How does the amount due compare with a budget of {b}?",
                "Against a {b} budget, how much does this order use?"]).format(b=money(budget)))
    return state, pool


def _ledger(rng, level):
    n = min(len(COUNTS) - 1, sround(3 + 1.6 * level, seed=rng.random()))
    transactions = [{"day": day, "type": rng.choice(["deposit", "withdrawal"]),
                     "amount": 5 * rng.randint(1, 10 + 10 * level)}
                    for day in sorted(rng.sample(range(1, 29), n))]
    signed = [t["amount"] if t["type"] == "deposit" else -t["amount"] for t in transactions]
    running = []
    for delta in signed:
        running.append((running[-1] if running else 0) + delta)
    start = max(0, 5 * round((-min(running) + rng.choice([-1, 1]) * 5 * rng.randint(1, 6)) / 5))
    balances = [start + r for r in running]
    final = balances[-1]
    flipped = rng.randrange(n)
    slips = [final - 2 * signed[flipped], final - signed[flipped], final - start, final + 10, final - 10,
             start - sum(signed)]

    sym = rng.choice(CURRENCIES)
    money = lambda v: f"{sym}{v}"
    style = rng.choice(["json", "table", "csv", "lines", "prose"])
    if style == "prose":
        body = " ".join(rng.choice(["On day {d}, a {t} of {a}.", "Day {d}: {t} of {a}."]).format(
            d=t["day"], t=t["type"], a=money(t["amount"])) for t in transactions)
        state = f"The account opens the month at {money(start)}. {body}"
    elif style == "json":
        state = json.dumps({"opening_balance": start, "currency": sym, "transactions": transactions},
                           ensure_ascii=False)
    else:
        state = f"Opening balance: {money(start)}\n{render_records(transactions, style)}"

    days = [f"day {t['day']}" for t in transactions]
    low_days = [d for d, b in zip(days, balances) if b == min(balances)]
    deposits = sum(t["type"] == "deposit" for t in transactions)
    change = final - start
    pool = {
        "went_negative": Decision(min(balances) < 0, type="noul", instructions=rng.choice([
            "Does the balance ever drop below zero?", "Is the account overdrawn at any point?"])),
        "withdrawal_count": Decision(n - deposits, type="score", criteria=COUNTS, instructions=rng.choice([
            "How many withdrawals are there?", "Count the withdrawals."])),
        "net_change": Decision(0 if change < -50 else 2 if change > 50 else 1, type="score", criteria=DRIFT,
            instructions=rng.choice(["From opening to closing, how did the balance change?",
                                     "Compare the final balance with the opening balance."])),
    }
    _likely(pool, "random_is_deposit", deposits, n, rng.choice([
        "If one transaction is picked uniformly at random, is it more likely than not to be a deposit?",
        "Is a randomly chosen transaction more likely than not a deposit?"]))
    if final >= 0:
        pool["final_balance"] = _numeric(rng, final, slips, money, rng.choice([
            "What is the balance after the last transaction?", "What is the closing balance?"]))
    if len(low_days) == 1:
        pool["lowest_day"] = Decision(low_days[0], criteria=dict.fromkeys(days), instructions=rng.choice([
            "After which day's transaction is the balance lowest?",
            "On which day does the balance reach its minimum?"]))
    return state, pool


def _clock(minutes):
    return f"{minutes // 60 % 24:02d}:{minutes % 60:02d}"


def _duration(minutes, rng):
    if minutes >= 60 and rng.random() < 0.5:
        hours, rest = divmod(minutes, 60)
        return f"{hours} h {rest} min" if rest else f"{hours} h"
    return f"{minutes} min"


def _schedule(rng, level):
    n = sround(2 + level + rng.random(), seed=rng.random())
    tasks = [{"task": name, "minutes": 5 * rng.randint(2, 9 + 3 * level)} for name in rng.sample(TASK_NAMES, n)]
    top = max(tasks, key=lambda t: t["minutes"])
    while sum(t["minutes"] == top["minutes"] for t in tasks) > 1:
        top["minutes"] += 5
    start = 5 * rng.randint(7 * 12, 13 * 12)
    gap = rng.choice([0, 0, 5, 10, 15]) if level >= 1 else 0
    starts, clock = [], start
    for t in tasks:
        starts.append(clock)
        clock += t["minutes"] + gap
    finish = clock - gap
    slips = [finish + gap, finish - (n - 1) * gap, finish - tasks[-1]["minutes"], finish + 60, finish - 60,
             finish + 10]

    rule = f"Tasks run back to back in this order{f', with a {gap}-minute break between tasks' if gap else ''}."
    rows = [{"task": t["task"], "duration": _duration(t["minutes"], rng)} for t in tasks]
    style = rng.choice(["table", "csv", "lines", "prose"])
    if style == "prose":
        body = ", then ".join(f"{r['task']} ({r['duration']})" for r in rows)
        state = f"Starting at {_clock(start)}: {body}. {rule}"
    else:
        state = f"Start: {_clock(start)}\n{render_records(rows, style)}\n\n{rule}"

    finish_time = _numeric(rng, finish, slips, _clock, rng.choice([
        "At what time does the last task end?", "When is everything finished?"]), offsets=(5, 10, 15, 30))
    deadline = _near(rng, finish, 5)
    long = rng.choice([20, 30, 45])
    pool = {
        "finish_time": finish_time,
        "done_by_deadline": Decision(finish <= deadline, type="noul", instructions=rng.choice([
            "Is everything done by {t}?", "Does the last task end at or before {t}?"]).format(t=_clock(deadline))),
        "longest_task": Decision(top["task"], criteria=dict.fromkeys(t["task"] for t in tasks), instructions=
            rng.choice(["Which task takes the longest?", "Which task is the longest?"])),
        "starts_before_noon": Decision(sum(s < 12 * 60 for s in starts), type="score", criteria=COUNTS,
            instructions=rng.choice(["How many tasks start before 12:00?",
                                     "Count the tasks that begin before noon."])),
    }
    _likely(pool, "random_is_long", sum(t["minutes"] > long for t in tasks), n, rng.choice([
        "If one task is picked uniformly at random, is it more likely than not to last more than {m} minutes?",
        "Is a randomly chosen task more likely than not to take longer than {m} minutes?"]).format(m=long))
    return state, pool


@dataclass
class PracticalArithmeticConfig(Config):
    def apply_difficulty(self, level):
        pass  # the generator reads the level


class PracticalArithmetic(Task):
    summary = "Exact arithmetic over an order, a ledger or a schedule, with distractor answers from typical slips."
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or PracticalArithmeticConfig())

    def generate_entry(self, state_seed=None, question=None):
        state_seed = random.randrange(2 ** 32) if state_seed is None else state_seed
        rng, level = random.Random(state_seed), min(self.config.level, 4)
        state, questions = rng.choice([_order, _ledger, _schedule])(rng, level)
        qid = question or random.choice(sorted(questions))
        return Entry({"payload": state, "state_seed": state_seed, "question_id": qid}, questions[qid])
