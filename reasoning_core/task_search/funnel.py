"""Where the pipeline loses proposals, one line per wave.

The logs say what each stage did; nothing said what the stages did to each other. A wave
that proposed 36 candidates and landed one task is either a strict gate, a weak proposer or
an implementor that keeps failing, and telling those apart meant reading three directories
by hand. This reads the same three the backlog does -- the archive is what was asked, the
package is what exists, the plans are what was attempted -- so it needs no state of its own
and cannot go stale.

    python -m reasoning_core.task_search.funnel
    python -m reasoning_core.task_search.funnel --why       # top rejection reasons
"""
import argparse
from collections import Counter
from pathlib import Path

import yaml

from .backlog import attempted, comparison_key, implemented
from .wave_proposer import _snake

STAGES = ("proposed", "accepted", "attempted", "landed")


def archive_waves(repo_root):
    root = Path(repo_root) / "reasoning_core" / "task_search" / "proposals" / "archive"
    for path in sorted(root.glob("*.yaml"), key=lambda item: item.stat().st_mtime):
        try:
            document = yaml.safe_load(path.read_text()) or {}
        except yaml.YAMLError:
            continue
        yield path.stem, document


def funnel(repo_root):
    """Per wave: how many ideas reached each stage, and why the rest stopped."""
    built, tried = implemented(repo_root), attempted(repo_root)
    for name, document in archive_waves(repo_root):
        accepted = document.get("proposals") or []
        rejected = document.get("rejected") or []
        keys = [comparison_key(_snake(item.get("name"))) for item in accepted]
        yield {
            "wave": name,
            "proposed": len(accepted) + len(rejected),
            "accepted": len(accepted),
            "attempted": sum(1 for key in keys if tried.get(key)),
            "landed": sum(1 for key in keys if key in built),
            "verdicts": Counter(item.get("verdict") or "?" for item in rejected),
            "reasons": Counter(_reason(item) for item in rejected),
        }


def _reason(rejection):
    """A rejection's cause, shortened to the part that differs between rejections."""
    reason = str(rejection.get("reason") or "").strip()
    for cut in (" samples judged it novel; ", "; "):
        if cut in reason:
            reason = reason.split(cut, 1)[1]
    return reason[:72] or "unstated"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--why", action="store_true",
                        help="also print the commonest rejection reasons")
    arguments = parser.parse_args(argv)

    rows = list(funnel(arguments.repo_root))
    if not rows:
        print("no archived waves")
        return 0
    width = max(len(row["wave"]) for row in rows)
    print(f"{'wave':<{width}}  " + "  ".join(f"{stage:>9}" for stage in STAGES))
    totals = Counter()
    for row in rows:
        totals.update({stage: row[stage] for stage in STAGES})
        print(f"{row['wave']:<{width}}  "
              + "  ".join(f"{row[stage]:>9}" for stage in STAGES))
    print(f"{'TOTAL':<{width}}  "
          + "  ".join(f"{totals[stage]:>9}" for stage in STAGES))

    # The drop between two stages is the one number that says which stage to work on.
    for earlier, later in zip(STAGES, STAGES[1:]):
        lost = totals[earlier] - totals[later]
        share = 100 * lost / totals[earlier] if totals[earlier] else 0
        print(f"  {earlier} -> {later}: {lost} lost ({share:.0f}%)")

    if arguments.why:
        verdicts, reasons = Counter(), Counter()
        for row in rows:
            verdicts.update(row["verdicts"])
            reasons.update(row["reasons"])
        print("\nrejection verdicts:",
              ", ".join(f"{name} {count}" for name, count in verdicts.most_common()))
        print("commonest reasons:")
        for reason, count in reasons.most_common(8):
            print(f"  {count:>4}  {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
