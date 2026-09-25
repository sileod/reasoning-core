import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_transfer_r4.plucker_chart_transfer.plucker_chart_transfer import (
    PluckerChartTransfer,
)

random.seed(3536382515)

OUT = Path(__file__).with_name("samples_P004v1.md")


def main():
    lines = []
    task = PluckerChartTransfer()
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            entry = task.generate_example(level=level)
            prompt = task.render_prompt(entry.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
