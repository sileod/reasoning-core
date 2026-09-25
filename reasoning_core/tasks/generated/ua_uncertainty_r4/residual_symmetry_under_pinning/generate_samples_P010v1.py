import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_uncertainty_r4.residual_symmetry_under_pinning import \
    residual_symmetry_under_pinning as mod


def main():
    random.seed(2409743872)
    task = mod.ResidualSymmetryUnderPinning()
    out = []
    for level in (0, 2, 5):
        out.append(f"# Level {level}")
        out.append("")
        for _ in range(2):
            ex = task.generate_example(level=level)
            out.append("Prompt:")
            out.append("")
            out.append(ex.prompt)
            out.append("")
            out.append(f"Answer: {ex.answer}")
            out.append("")
    path = Path(__file__).with_name("samples_P010v1.md")
    path.write_text("\n".join(out), encoding="utf-8")
    print(path.resolve())


if __name__ == "__main__":
    main()
