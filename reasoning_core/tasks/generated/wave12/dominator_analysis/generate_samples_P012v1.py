"""Generate samples_P012v1.md for the dominator_analysis trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.dominator_analysis.dominator_analysis import (
    DominatorAnalysis,
)

random.seed(2707068757)

OUT = Path(__file__).with_name("samples_P012v1.md")


def main():
    task = DominatorAnalysis()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}\n")
        want = {"yes", "no"}
        got = set()
        while len(got) < 2:
            e = task.generate_example()
            if e.answer in want:
                lines.append("### Example\n")
                lines.append(task.render_prompt(e.metadata))
                lines.append("")
                lines.append(f"Answer: {e.answer}")
                lines.append("")
                want.discard(e.answer)
                got.add(e.answer)
        lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
