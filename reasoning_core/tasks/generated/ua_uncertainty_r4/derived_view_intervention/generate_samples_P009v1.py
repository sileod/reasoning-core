import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.derived_view_intervention.derived_view_intervention import (
    DerivedViewIntervention,
)

SEED = 3867019559

OUT = Path(__file__).with_name("samples_P009v1.md")


def main():
    random.seed(SEED)
    task = DerivedViewIntervention()
    lines = ["# samples_P009v1", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for idx in (1, 2):
            ex = task.generate_example()
            lines.append(f"### Example {idx}")
            lines.append("")
            lines.append("Prompt:")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
