import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.instruction_priority.instruction_priority import (
    InstructionPriority,
)

SEED = 1002768851
OUT = Path(__file__).with_name("samples_P001v1.md")

LEVELS = [0, 2, 5]
PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = InstructionPriority()
    lines = []
    lines.append("# Samples: instruction_priority (P001v1)")
    lines.append("")
    for level in LEVELS:
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(PER_LEVEL):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            for pl in prompt.split("\n"):
                lines.append(f"    {pl}")
            lines.append("")
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
