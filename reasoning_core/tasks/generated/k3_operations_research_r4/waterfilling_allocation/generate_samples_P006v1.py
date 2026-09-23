import random
from pathlib import Path

random.seed(798610012)

from reasoning_core.tasks.generated.k3_operations_research_r4.maxmin_waterfilling_allocation.waterfilling_alloc import (
    WaterfillingAllocation,
)


def main():
    task = WaterfillingAllocation()
    out = Path(__file__).with_name("samples_P006v1.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            lines.append("### Example %d" % (i + 1))
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
