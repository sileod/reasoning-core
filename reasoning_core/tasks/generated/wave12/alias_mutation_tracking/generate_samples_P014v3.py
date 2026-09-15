import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.alias_mutation_tracking.alias_mutation_tracking import (
    AliasMutationTracking,
)

random.seed(3725686066)

OUT = Path(__file__).with_name("samples_P014v3.md")


def main():
    task = AliasMutationTracking()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(2):
            e = task.generate_example()
            lines.append("### Prompt")
            lines.append(e.metadata["prompt"])
            lines.append("### Answer")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
