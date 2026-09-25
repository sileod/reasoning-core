from pathlib import Path

import random

from reasoning_core.tasks.generated.ua_state_tracking_r5.mean_preserving_spread_order.mean_preserving_spread_order import (
    MeanPreservingSpreadOrder,
)

random.seed(241712510)

OUT = Path(__file__).with_name("samples_P007v2.md")


def main():
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        task = MeanPreservingSpreadOrder()
        task.config.set_level(level)
        for _ in range(2):
            ex = task.generate_example()
            lines.append("Prompt:")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
