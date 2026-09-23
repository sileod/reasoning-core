import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_state_tracking_r4.misra_gries_summary.misra_gries_summary import (
    MisraGriesSummary,
)

OUT = Path(__file__).with_name("samples_P007v2.md")


def main():
    random.seed(241712510)
    task = MisraGriesSummary()
    lines = ["# Samples for misra_gries_summary (P007v2)", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d" % level)
        lines.append("")
        for i in range(2):
            entry = task.generate_example()
            lines.append("### Example %d" % (i + 1))
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
