"""Generate samples_P008v3.md for the ConcurrentEditRebase task."""
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from concurrent_edit_rebase import ConcurrentEditRebase

SEED = 1618848011
OUT = Path(__file__).with_name("samples_P008v3.md")


def main():
    random.seed(SEED)
    task = ConcurrentEditRebase()
    lines = ["# ConcurrentEditRebase samples (P008v3)", ""]
    for level in (0, 2, 5):
        lines.append("## Level %d" % level)
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            e = task.generate_example()
            lines.append(task.render_prompt(e.metadata))
            lines.append("")
            lines.append("Answer: %s" % e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote %s" % OUT)


if __name__ == "__main__":
    main()
