"""Manipulate quantities written in mixed or irregular units: clock time, durations, calendar dates
and weekdays, compass headings, imperial and metric lengths, mass, volume and money.

One procedure throughout: convert to a base unit, do the arithmetic (carries, borrows, wrap-around,
month lengths, leap years), and write the result back in the asked format. A step offsets, scales,
converts or takes a difference; each step feeds the next, and level adds steps. Conversions are
exact integers, so answers never need decimals.
"""
import calendar
import datetime as dt
import random
import re
from dataclasses import dataclass

from reasoning_core.template import Config, DevTask, Entry, stochastic_rounding as sround

DAYS = list(calendar.day_name)
MONTHS = list(calendar.month_name)[1:]


@dataclass
class UnitManipulationConfig(Config):
    steps: float = 1
    span: int = 3

    def apply_difficulty(self, level):
        self.steps += 0.8 * level
        self.span += 3 * level


# ---- unit systems: base-unit integers, rendered in mixed units ---------------------------------

SYSTEMS = {  # name: (units largest first, as (name, size in base units)), plural forms are s-suffixed
    "length_imperial": [("mi", 63360), ("yd", 36), ("ft", 12), ("in", 1)],
    "length_metric": [("km", 1000000), ("m", 1000), ("cm", 10), ("mm", 1)],
    "mass": [("lb", 16), ("oz", 1)],
    "volume": [("gal", 16), ("qt", 4), ("pt", 2), ("cup", 1)],
    "duration": [("d", 86400), ("h", 3600), ("min", 60), ("s", 1)],
    "money": [("dollars", 100), ("cents", 1)],
}


def mixed(system, base, units=None):
    """Render base units as e.g. '3 ft 4 in', using `units` (default: all units of the system)."""
    if base == 0:
        return f"0 {SYSTEMS[system][-1][0]}"
    parts, rest = [], base
    for name, size in SYSTEMS[system]:
        if units and name not in units:
            continue
        k, rest = divmod(rest, size)
        if k:
            parts.append(f"{k} {name}")
    return " ".join(parts)


def parse_mixed(system, text):
    sizes = dict(SYSTEMS[system])
    alias = {"minutes": "min", "minute": "min", "mins": "min", "hours": "h", "hour": "h", "hr": "h", "hrs": "h",
             "days": "d", "day": "d", "seconds": "s", "second": "s", "sec": "s", "secs": "s",
             "feet": "ft", "foot": "ft", "inches": "in", "inch": "in", "yards": "yd", "yard": "yd",
             "miles": "mi", "mile": "mi", "pounds": "lb", "lbs": "lb", "ounces": "oz", "cups": "cup",
             "pints": "pt", "quarts": "qt", "gallons": "gal", "dollar": "dollars", "cent": "cents"}
    pairs = re.findall(r"(\d+)\s*([a-z]+)", text.lower())
    if not pairs or re.sub(r"(\d+)\s*([a-z]+)|\s|and|,", "", text.lower()):
        return None
    total = 0
    for k, unit in pairs:
        unit = alias.get(unit, unit)
        if unit not in sizes:
            return None
        total += int(k) * sizes[unit]
    return total


def _amount(system, rng, span):
    """A random quantity of `system` spanning a few of its units."""
    units = SYSTEMS[system]
    top = rng.randint(0, min(len(units) - 1, 1 + span // 3))
    hi = units[top][1] * rng.randint(1, 2 + span)
    return rng.randint(units[-1][1], hi)


# ---- steps ---------------------------------------------------------------------------------------

def _amount_steps(system, x, rng, span):
    """Steps on a plain quantity: (sentence, new value)."""
    d = _amount(system, rng, span)
    out = [(f"add {mixed(system, d)}", x + d)]
    if x > d:
        out.append((f"take away {mixed(system, d)}", x - d))
    k = rng.randint(2, 3 + span // 2)
    if x * k < 10 ** 7:
        out.append((f"multiply by {k}", x * k))
    if x % k == 0 and x // k:
        out.append((f"split into {k} equal parts and keep one", x // k))
    return out


def _datetime_steps(t, rng, span, with_time):
    out = []
    days = rng.randint(1, 10 * span)
    out.append((f"move forward {days} day{'s' * (days > 1)}", t + dt.timedelta(days=days)))
    out.append((f"move back {days} day{'s' * (days > 1)}", t - dt.timedelta(days=days)))
    weeks = rng.randint(1, 2 + span)
    out.append((f"move forward {weeks} week{'s' * (weeks > 1)}", t + dt.timedelta(weeks=weeks)))
    months = rng.randint(1, 2 + span)
    y, m = divmod(t.month - 1 + months, 12)
    day = min(t.day, calendar.monthrange(t.year + y, m + 1)[1])
    out.append((f"move forward {months} calendar month{'s' * (months > 1)} (keeping the day, or the "
                f"month's last day if it is shorter)", t.replace(year=t.year + y, month=m + 1, day=day)))
    if with_time:
        secs = max(60, _amount("duration", rng, span) // 60 * 60)
        out.append((f"move forward {mixed('duration', secs)}", t + dt.timedelta(seconds=secs)))
        out.append((f"move back {mixed('duration', secs)}", t - dt.timedelta(seconds=secs)))
    return out


def _fmt_dt(t, with_time):
    s = f"{DAYS[t.weekday()]} {t.day} {MONTHS[t.month - 1]} {t.year}"
    return s + f", {t:%H:%M}" if with_time else s


# ---- questions -----------------------------------------------------------------------------------

def _quantity_problem(rng, want, span):
    system = rng.choice(list(SYSTEMS))
    x = _amount(system, rng, span)
    lines = [f"Start with {mixed(system, x)}."]
    for _ in range(want):
        text, x = rng.choice(_amount_steps(system, x, rng, span))
        lines.append(f"Then {text}.")
    units = SYSTEMS[system]
    # Sometimes ask for two adjacent units only (e.g. feet and inches), when that stays a short number.
    pairs = [i for i in range(len(units) - 1) if x < 1000 * units[i][1] and x % units[i + 1][1] == 0
             and any(units[j][1] <= x for j in range(i))]
    if pairs and rng.random() < 0.5:
        i = rng.choice(pairs)
        keep = [units[i][0], units[i + 1][0]]
        return lines, f"Write the result using only {keep[0]} and {keep[1]}.", mixed(system, x, keep), system
    return lines, "Write the result in mixed units, largest first, omitting zero parts.", mixed(system, x), system


def _calendar_problem(rng, want, span):
    with_time = rng.random() < 0.5
    t = dt.datetime(rng.randint(1990, 2040), rng.randint(1, 12), rng.randint(1, 28),
                    rng.randint(0, 23) if with_time else 0, rng.choice(range(0, 60, 5)) if with_time else 0)
    lines = [f"Start at {_fmt_dt(t, with_time)}."]
    for _ in range(want):
        text, t = rng.choice(_datetime_steps(t, rng, span, with_time))
        lines.append(f"Then {text}.")
    ask = rng.choice(["weekday", "date", "full"] if not with_time else ["weekday", "time", "full"])
    if ask == "weekday":
        return lines, "Which day of the week is it? Answer with the weekday name.", DAYS[t.weekday()], "weekday"
    if ask == "time":
        return lines, "What time is it? Answer as HH:MM in 24-hour format.", f"{t:%H:%M}", "time"
    if with_time:
        return lines, "Where are you now? Answer as YYYY-MM-DD HH:MM.", f"{t:%Y-%m-%d %H:%M}", "datetime"
    return lines, "What is the date now? Answer as YYYY-MM-DD.", f"{t:%Y-%m-%d}", "date"


def _heading_problem(rng, want, span):
    h = rng.randrange(0, 360, 5)
    lines = [f"A ship's heading is {h} degrees (0 is north, angles grow clockwise)."]
    for _ in range(want):
        a = rng.randrange(5, 360, 5)
        side = rng.choice(["right", "left"])
        h = (h + a) % 360 if side == "right" else (h - a) % 360
        lines.append(f"It turns {a} degrees to the {side}.")
    return lines, "What is its heading now? Answer with an integer from 0 to 359.", str(h), "heading"


def _difference_problem(rng, want, span):
    a = dt.date(rng.randint(1990, 2040), rng.randint(1, 12), rng.randint(1, 28))
    b = a + dt.timedelta(days=rng.randint(1, 40 * span * max(1, want)))
    return ([f"One event is on {a.day} {MONTHS[a.month - 1]} {a.year} and another on {b.day} "
             f"{MONTHS[b.month - 1]} {b.year}."],
            "How many days after the first is the second? Answer with an integer.", str((b - a).days), "int")


class UnitManipulation(DevTask):
    summary = ("Convert, offset, scale and compare quantities in mixed or irregular units: clock time, "
               "durations, calendar dates and weekdays, headings, lengths, mass, volume and money.")
    task_version = 1

    def __init__(self, config=None):
        super().__init__(config=config or UnitManipulationConfig())

    def generate_entry(self):
        c, rng = self.config, random
        want = max(1, sround(c.steps))
        maker = rng.choice([_quantity_problem, _quantity_problem, _calendar_problem, _calendar_problem,
                            _heading_problem, _difference_problem])
        lines, ask, answer, kind = maker(rng, want, c.span)
        return Entry({"lines": lines, "ask": ask, "kind": kind}, answer)

    def render_prompt(self, m):
        return " ".join(m["lines"]) + "\n" + m["ask"]

    def score_answer(self, answer, entry):
        kind, gold = entry.metadata["kind"], str(entry.answer)
        got = str(answer).strip().strip(".").strip()
        if kind in SYSTEMS:
            return float(parse_mixed(kind, got) == parse_mixed(kind, gold) and parse_mixed(kind, got) is not None)
        if kind == "weekday":
            return float(got.lower() == gold.lower())
        if kind == "time":
            m = re.fullmatch(r"(\d{1,2}):(\d{2})\s*([ap]\.?m\.?)?", got.lower())
            if not m:
                return 0.0
            h = int(m.group(1))
            if m.group(3):
                h = h % 12 + 12 * m.group(3).startswith("p")
            return float(f"{h:02d}:{m.group(2)}" == gold)
        return float(" ".join(got.split()) == gold)
