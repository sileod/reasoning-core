"""Generate samples_P005v1.md for centering_transition_tracking."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.centering_transition_tracking import (
    centering_transition_tracking as mod,
)

SEED = 729651269
LEVELS = (0, 2, 5)


def main():
    random.seed(SEED)
    out = Path(__file__).with_name("samples_P005v1.md")
    task = mod.CenteringTransitionTracking()
    lines = []
    for level in LEVELS:
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for i in range(2):
            entry = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("Prompt:")
            lines.append(entry.metadata["_prompt"] if "_prompt" in entry.metadata
                         else task.render_prompt(entry.metadata))
            lines.append("Answer:")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
