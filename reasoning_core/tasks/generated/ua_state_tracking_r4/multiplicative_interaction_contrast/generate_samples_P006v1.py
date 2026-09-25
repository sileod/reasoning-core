import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.multiplicative_interaction_contrast.multiplicative_interaction_contrast import (
    MultiplicativeInteractionContrast,
)

SEED = 798610012


def main():
    random.seed(SEED)
    out = Path(__file__).with_name("samples_P006v1.md")
    lines = []
    levels = [0, 2, 5]
    for level in levels:
        lines.append(f"## Level {level}")
        task = MultiplicativeInteractionContrast()
        task.config.set_level(level)
        for k in range(2):
            entry = task.generate_example()
            lines.append(f"### Example {k + 1}")
            lines.append("**Prompt**")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
