import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.dynamic_lot_sizing_plan.dynamic_lot_sizing_plan import (
    DynamicLotSizingPlan,
)

SEED = 729651269
OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    random.seed(SEED)
    task = DynamicLotSizingPlan()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(2):
            entry = task.generate_entry()
            lines.append("")
            lines.append("**Prompt:**")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append(entry.answer)
        lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
