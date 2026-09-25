import random
from pathlib import Path

random.seed(682015719)

from reasoning_core.tasks.generated.ua_latent_representation_r4.experiment_garbling_order.experiment_garbling_order import (
    ExperimentGarblingOrder,
)


def main():
    task = ExperimentGarblingOrder()
    out = Path(__file__).with_name("samples_P008v1.md")
    lines = ["# Samples for experiment_garbling_order (P008v1)", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Level {level} example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"`{ex.answer}`")
            lines.append("")
    out.write_text("\n".join(lines))
    print(out)


if __name__ == "__main__":
    main()
