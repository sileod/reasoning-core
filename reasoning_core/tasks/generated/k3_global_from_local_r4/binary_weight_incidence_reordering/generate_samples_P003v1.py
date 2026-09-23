import random
from pathlib import Path

from binary_weight_incidence_reordering import BinaryWeightIncidenceReordering

random.seed(2267388306)

LEVELS = [(0, 2), (2, 2), (5, 2)]


def main():
    task = BinaryWeightIncidenceReordering()
    lines = []
    for level, count in LEVELS:
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(count):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {x.answer}")
            lines.append("")
    out = Path(__file__).with_name("samples_P003v1.md")
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
