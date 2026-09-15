import random
from pathlib import Path

from reasoning_core.tasks.generated.manual_high_value_80_r1.modular_constraint_solver.modular_constraint_solver import (
    ModularConstraintSolver,
)

SEED = 3715178603
OUT = Path(__file__).with_name("samples_P061v1.md")


def main():
    random.seed(SEED)
    lines = [
        "# Samples P061v1: modular_constraint_solver",
        "",
        "Each instance gives a system of modular congruences and asks for the canonical "
        "('R mod M') solution or 'inconsistent'.",
        "",
    ]
    for level in (0, 2, 5):
        lines.append("## Level %d" % level)
        lines.append("")
        t = ModularConstraintSolver()
        t.config.set_level(level)
        for _ in range(2):
            x = t.generate_example()
            lines.append("**Example**")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(t.render_prompt(x.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:** `%s`" % x.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
