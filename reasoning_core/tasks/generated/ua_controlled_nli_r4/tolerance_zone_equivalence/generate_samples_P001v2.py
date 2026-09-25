import random
from pathlib import Path

random.seed(2302342651)

from reasoning_core.tasks.generated.ua_controlled_nli_r4.tolerance_zone_equivalence.tolerance_zone_equivalence import (
    ToleranceZoneEquivalence,
)

OUT = Path(__file__).with_name("samples_P001v2.md")


def main():
    task = ToleranceZoneEquivalence()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for k in (1, 2):
            entry = task.generate_example()
            lines.append(f"### Example {k}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(entry.metadata.get("_prompt", task.render_prompt(entry.metadata)))
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
