import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.phase_change_equilibration import (
    phase_change_equilibration as m,
)


def main():
    random.seed(382564971)
    out = Path(__file__).with_name("samples_P003v2.md")
    task = m.PhaseChangeEquilibration()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for _ in range(2):
            x = task.generate_example()
            lines.append("Prompt:")
            lines.append(task.render_prompt(x.metadata))
            lines.append("Answer:")
            lines.append(x.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
