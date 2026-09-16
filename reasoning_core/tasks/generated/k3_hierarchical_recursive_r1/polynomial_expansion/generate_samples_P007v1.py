import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.polynomial_expansion.polynomial_expansion import (
    PolynomialExpansion,
)

SEED = 1139467751
OUT = Path(__file__).with_name("samples_P007v1.md")

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    task = PolynomialExpansion()
    lines = ["# Samples P007v1", ""]
    for level, count in LEVELS.items():
        lines.append(f"## Level {level}")
        lines.append("")
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(count):
            x = task.generate_example()
            lines.append("### Prompt")
            lines.append("")
            lines.append(task.render_prompt(x.metadata))
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    random.seed(SEED)
    main()
