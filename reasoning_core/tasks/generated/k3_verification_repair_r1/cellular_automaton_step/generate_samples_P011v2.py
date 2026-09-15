import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.cellular_automaton_step.cellular_automaton_step import (
    CellularAutomatonStep,
)

SEED = 525660630


def main():
    random.seed(SEED)
    out = Path(__file__).with_name("samples_P011v2.md")
    task = CellularAutomatonStep()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        task.config.set_level(level)
        for _ in range(2):
            x = task.generate_example()
            lines.append("### Prompt")
            lines.append("")
            lines.append(task.render_prompt(x.metadata))
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
