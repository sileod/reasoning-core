import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_counterfactual_r4.which_path_intervention.which_path_intervention import (
    WhichPathIntervention,
)

SEED = 798610012
OUT = Path(__file__).with_name("samples_P006v1.md")


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        task = WhichPathIntervention()
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for i in range(2):
            e = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("Prompt:")
            lines.append("")
            lines.append(f"> {task.render_prompt(e.metadata)}")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(f"> {e.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
