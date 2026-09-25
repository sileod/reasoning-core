"""Generate samples_P002v1.md for the strategy_realization_equivalence trial.

Seeded (seed=1475571465) so the file is byte-reproducible across processes.
"""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_state_tracking_r4.strategy_realization_equivalence.strategy_realization_equivalence import (
    StrategyRealizationEquivalence,
)


def main():
    random.seed(1475571465)
    task = StrategyRealizationEquivalence()
    out_path = Path(__file__).with_name("samples_P002v1.md")

    lines = [
        "# Samples: strategy_realization_equivalence (P002v1)",
        "",
        "Each example gives a full binary decision tree's all-Left history as a",
        "list of nodes, and asks for the reduced-fraction realization probability.",
        "",
    ]

    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append("Prompt:")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
