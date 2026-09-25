import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.fermionic_normal_ordering.fermionic_normal_ordering import (
    FermionicNormalOrdering,
)

SEED = 2409743872


def main():
    random.seed(SEED)
    task = FermionicNormalOrdering()
    out = Path(__file__).with_name("samples_P010v1.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            x = task.generate_example()
            lines.append("### Prompt")
            lines.append("")
            lines.append(task.render_prompt(x.metadata))
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
