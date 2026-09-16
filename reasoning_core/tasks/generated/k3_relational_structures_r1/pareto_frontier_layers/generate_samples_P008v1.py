import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relational_structures_r1.pareto_frontier_layers.pareto_frontier_layers import (
    ParetoFrontierLayers,
)

SEED = 682015719
OUT = Path(__file__).with_name("samples_P008v1.md")


def main():
    random.seed(SEED)
    task = ParetoFrontierLayers()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        for _ in range(2):
            task.config.set_level(level)
            e = task.generate_example()
            lines.append("PROMPT:")
            lines.append(task.render_prompt(e.metadata))
            lines.append("Answer: " + e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
