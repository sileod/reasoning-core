import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.redundant_signal_race_bounds.redundant_signal_race_bounds import (
    RedundantSignalRaceBounds,
)

SEED = 2267388306
OUT = Path(__file__).with_name("samples_P003v1.md")


def main():
    random.seed(SEED)
    task = RedundantSignalRaceBounds()
    levels = (0, 2, 5)
    lines = ["# Samples for P003v1: redundant_signal_race_bounds", ""]
    for level in levels:
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"### Level {level} example {i+1}")
            lines.append("")
            lines.append("**Prompt**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
