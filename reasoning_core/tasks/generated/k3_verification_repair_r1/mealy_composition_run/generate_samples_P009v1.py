import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.mealy_composition_run.mealy_composition_run import (
    MealyCompositionRun,
)

OUT = Path(__file__).with_name("samples_P009v1.md")


def main():
    task = MealyCompositionRun()
    parts = []
    for level in (0, 2, 5):
        parts.append(f"## Level {level}")
        for k in range(2):
            ex = task.generate_example(level=level)
            parts.append(f"### Example {k + 1}")
            parts.append("**Prompt:**")
            parts.append("```")
            parts.append(ex.prompt)
            parts.append("```")
            parts.append("**Answer:**")
            parts.append("```")
            parts.append(ex.answer)
            parts.append("```")
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    random.seed(3867019559)
    main()
