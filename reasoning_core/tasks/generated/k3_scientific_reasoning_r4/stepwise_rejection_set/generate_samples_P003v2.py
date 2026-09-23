import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.stepwise_rejection_set.stepwise_rejection_set import (
    StepwiseRejectionSet,
)

SEED = 382564971
LEVELS = (0, 2, 5)
EXAMPLES_PER_LEVEL = 2


def main():
    random.seed(SEED)
    task = StepwiseRejectionSet()
    lines = []
    for level in LEVELS:
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for _ in range(EXAMPLES_PER_LEVEL):
            ex = task.generate_example()
            lines.append("### Example")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out = Path(__file__).with_name("samples_P003v2.md")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
