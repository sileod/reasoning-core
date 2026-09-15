import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.euler_tour_intervals.euler_tour_intervals import (
    EulerTourIntervals,
)

SEED = 1475571465
OUT = Path(__file__).with_name("samples_P002v1.md")


def main():
    random.seed(SEED)
    task = EulerTourIntervals()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        task.config.set_level(level)
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(prompt)
            lines.append(f"Answer: {entry.answer}")
            lines.append("")
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
