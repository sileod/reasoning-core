import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_specific_r1.elliptic_curve_scalar_mul.elliptic_curve_scalar_mul import (
    EllipticCurveScalarMul,
)

SEED = 729651269
OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task = EllipticCurveScalarMul()
        task.config.set_level(level)
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append("**Prompt:**")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append(entry.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
