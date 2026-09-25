"""Generate samples_P005v1.md for the optimality-theory tableau task."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.optimality_theory_tableau_ranking.optimality_theory_tableau_ranking import (
    OptimalityTheoryTableauRanking,
)

SEED = 729651269
OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    random.seed(SEED)
    task = OptimalityTheoryTableauRanking()
    lines = ["# Samples P005v1: optimality_theory_tableau_ranking", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
