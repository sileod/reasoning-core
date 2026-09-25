import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.free_cumulant_recovery.free_cumulant_recovery import (
    FreeCumulantRecovery,
)

OUT = Path(__file__).with_name("samples_P007v2.md")

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(241712510)
    lines = ["# Samples for P007v2 (free_cumulant_recovery)", ""]
    task = FreeCumulantRecovery()
    for level, count in LEVELS.items():
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(count):
            ex = task.generate_example(level=level)
            lines.append("### Prompt")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(f"`{ex.answer}`")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
