import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_language_implementation_r4.query_cardinality_estimation.query_cardinality_estimation import (
    QueryCardinalityEstimation,
)

SEED = 1139467751
LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    task = QueryCardinalityEstimation()
    lines = []
    for level in sorted(LEVELS):
        lines.append(f"Level {level}")
        for _ in range(LEVELS[level]):
            task.config.set_level(level)
            ex = task.generate_example()
            lines.append("Prompt:")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("Answer")
            lines.append(ex.answer)
        lines.append("")
    out = Path(__file__).with_name("samples_P007v1.md")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
