import random
from dataclasses import dataclass
from datetime import date, timedelta

from reasoning_core.template import Config, Entry, Task


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

TASK_META = {'parent_source_id': None,
 'idea': 'calendar_recurrence_execution (draw 1 of 3)',
 'hypothesis': 'manual_high_value_80:calendar_recurrence_execution',
 'changes': 'new task in '
            'reasoning_core/tasks/generated/wave12/calendar_recurrence_execution',
 'generation': {'provider_name': 'albert',
                'model_name': 'deepseek-v4-flash',
                'harness_name': 'opencode',
                'harness_version': None,
                'agent_name': 'task-search-worker',
                'settings': {'variant': None,
                             'requested_seed': 4088891760,
                             'seed_forwarded': True,
                             'temperature': None,
                             'top_p': None,
                             'pure': True,
                             'max_steps': 40,
                             'timeout_seconds': 1800,
                             'sandbox': {'name': 'bubblewrap',
                                         'version': 'bubblewrap 0.8.0'}}}}


def _isoweekday_to_index(day: str) -> int:
    return {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}[day]


WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def iter_dates(start: date, end: date):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def nth_valid_date(start: date, end: date, base: list, exclusions: list, adjustments: dict):
    count = 0
    for d in iter_dates(start, end):
        valid = d.weekday() in base
        if valid and any(a <= d <= b for a, b in exclusions):
            valid = False
        if valid and d in adjustments:
            valid = adjustments[d]
        if valid:
            count += 1
    return count


@dataclass
class CalendarRecurrenceConfig(Config):
    n: int = 2
    span_days: int = 90
    num_days: int = 2

    def apply_difficulty(self, level):
        self.n = 1 + min(level, 4)
        self.span_days = 60 + 30 * level
        self.num_days = min(7, max(2, 2 + level))


class CalendarRecurrenceExecution(Task):
    summary = "Generate occurrences from explicit recurrence, exclusion, and adjustment rules, returning the nth valid date as YYYY-MM-DD with n varying per instance."
    design_choice = "return the nth valid date as YYYY-MM-DD for a fixed n, with n varying per instance (e.g., 1 to 5)"
    config_cls = CalendarRecurrenceConfig

    def _build(self):
        cfg = self.config
        n = cfg.n
        num_days = cfg.num_days
        start = date(2024, 1, 1) + timedelta(days=random.randrange(0, 366))
        end = start + timedelta(days=cfg.span_days)

        days = random.sample(range(7), num_days)
        base = set(days)

        exclusion_count = random.randrange(0, 3)
        exclusions = []
        points = sorted(random.sample(range(0, cfg.span_days + 1), min(max(2, 2 * exclusion_count) if exclusion_count else 0, cfg.span_days + 1)))
        for i in range(exclusion_count):
            a = points[2 * i]
            b = points[2 * i + 1]
            exclusions.append((start + timedelta(days=a), start + timedelta(days=b)))

        adjustment_count = random.randrange(0, 2)
        adjustments = {}
        for _ in range(adjustment_count):
            dy = random.randrange(0, cfg.span_days + 1)
            d = start + timedelta(days=dy)
            if d.weekday() in base:
                adjustments[d] = False

        total = nth_valid_date(start, end, base, exclusions, adjustments)
        needed = n
        attempts = 0
        while needed > total and attempts < 50:
            attempts += 1
            start = date(2024, 1, 1) + timedelta(days=random.randrange(0, 366))
            end = start + timedelta(days=cfg.span_days)
            base = set(random.sample(range(7), num_days))
            exclusions = []
            points = sorted(random.sample(range(0, cfg.span_days + 1), min(max(2, 2 * exclusion_count) if exclusion_count else 0, cfg.span_days + 1)))
            for i in range(exclusion_count):
                a = points[2 * i]
                b = points[2 * i + 1]
                exclusions.append((start + timedelta(days=a), start + timedelta(days=b)))
            adjustments = {}
            for _ in range(adjustment_count):
                dy = random.randrange(0, cfg.span_days + 1)
                d = start + timedelta(days=dy)
                if d.weekday() in base:
                    adjustments[d] = False
            total = nth_valid_date(start, end, base, exclusions, adjustments)
        if needed > total:
            raise RuntimeError("could not build instance with enough valid dates")

        count = 0
        nth = None
        for d in iter_dates(start, end):
            valid = d.weekday() in base
            if valid and any(a <= d <= b for a, b in exclusions):
                valid = False
            if valid and d in adjustments:
                valid = adjustments[d]
            if valid:
                count += 1
                if count == n:
                    nth = d
                    break
        return start, end, base, exclusions, adjustments, nth

    def generate_entry(self):
        start, end, base, exclusions, adjustments, nth = self._build()
        assert nth is not None
        base_days = [WEEKDAYS[i] for i in sorted(base)]
        exc_str = "; ".join(
            f"{a.strftime('%Y-%m-%d')} to {b.strftime('%Y-%m-%d')}" for a, b in exclusions
        )
        adj_str = "; ".join(d.strftime("%Y-%m-%d") for d in sorted(adjustments))
        metadata = {
            "start": start.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "days": base_days,
            "exclusions": exc_str,
            "adjustments": adj_str,
            "n": int(self.config.n),
        }
        return Entry(metadata=metadata, answer=nth.strftime("%Y-%m-%d"))

    def render_prompt(self, metadata):
        lines = [
            f"An event recurs weekly on: {', '.join(metadata['days'])}.",
        ]
        if metadata["exclusions"]:
            lines.append(f"It is cancelled on: {metadata['exclusions']}.")
        if metadata["adjustments"]:
            lines.append(f"It is additionally cancelled on: {metadata['adjustments']}.")
        lines.append(
            f"The first occurrence is on or after {metadata['start']} through {metadata['end']}."
        )
        lines.append(
            f"What is the {_ordinal(metadata['n'])} occurrence date? Answer as YYYY-MM-DD."
        )
        return "\n".join(lines)
