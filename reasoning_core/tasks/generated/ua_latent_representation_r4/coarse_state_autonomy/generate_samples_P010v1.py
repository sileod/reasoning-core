import random
from pathlib import Path

random.seed(2409743872)

from reasoning_core.tasks.generated.ua_latent_representation_r4.coarse_state_autonomy.coarse_state_autonomy import (
    CoarseStateAutonomy,
)

OUT = Path(__file__).with_name("samples_P010v1.md")

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    task = CoarseStateAutonomy()
    lines = []
    for level, count in LEVELS.items():
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for i in range(count):
            e = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("**Prompt**")
            lines.append("```")
            lines.append(task.render_prompt(e.metadata))
            lines.append("```")
            lines.append("**Answer**")
            lines.append("```")
            lines.append(e.answer)
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
