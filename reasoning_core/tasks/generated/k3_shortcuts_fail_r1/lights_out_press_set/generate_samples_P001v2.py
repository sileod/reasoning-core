import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.lights_out_press_set.lights_out_press_set import (
    LightsOutPressSet,
)

SEED = 2302342651
OUT = Path(__file__).with_name("samples_P001v2.md")


def main():
    random.seed(SEED)
    task = LightsOutPressSet()
    lines = []
    lines.append("# LightsOutPressSet samples")
    lines.append("")
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(ex.prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
