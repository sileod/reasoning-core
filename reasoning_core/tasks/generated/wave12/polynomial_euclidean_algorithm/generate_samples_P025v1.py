import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.polynomial_euclidean_algorithm.polynomial_euclidean_algorithm import (
    PolynomialEuclideanAlgorithm,
)


def main():
    random.seed(924413700)
    out_path = Path(__file__).with_name("samples_P025v1.md")
    lines = []
    task = PolynomialEuclideanAlgorithm()
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"# Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append("## Prompt")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("## Answer")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
