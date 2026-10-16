"""A provider-agnostic cap on what workers spend, read from the harness's own step costs.

opencode prices every step it finishes (`step_finish.part.cost`), whichever provider
answered. A free provider reports 0 and never moves the ledger, so the default cap of
0 USD costs nothing on Albert and stops a run the moment a paid key is being spent.
Only opencode reports cost, and a custom provider without a price table reports 0 too:
this catches a key routed somewhere priced, not every possible bill.
"""

import json
import os
from pathlib import Path

LEDGER = Path.home() / ".local" / "share" / "reasoning_core" / "worker_spend.tsv"
BUDGET_VAR = "TASK_SEARCH_BUDGET_USD"


def budget():
    return float(os.environ.get(BUDGET_VAR) or 0)


def spent(ledger=LEDGER):
    if not Path(ledger).exists():
        return 0.0
    return sum(float(line.split("\t")[1]) for line in Path(ledger).read_text().splitlines()
               if line.count("\t") == 1)


def over(extra=0.0, ledger=LEDGER):
    return spent(ledger) + extra > budget()


def trial_cost(events_path):
    """Dollars a trial has spent so far; tolerates the half-written last line of a live log."""
    total = 0.0
    try:
        lines = Path(events_path).read_text().splitlines()
    except FileNotFoundError:
        return total
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict) and event.get("type") == "step_finish":
            total += float((event.get("part") or {}).get("cost") or 0)
    return total


def record(label, cost, ledger=LEDGER):
    if cost > 0:
        Path(ledger).parent.mkdir(parents=True, exist_ok=True)
        with Path(ledger).open("a") as handle:
            handle.write(f"{label}\t{cost}\n")
