import random
from pathlib import Path

from censoring_observation_equivalence import CensoringObservationEquivalence

random.seed(1259343118)
OUT = Path(__file__).with_name("samples_P003v3.md")


def gen(task, level):
    task.config.set_level(level)
    xs = [task.generate_example() for _ in range(2)]
    return xs


def main():
    task = CensoringObservationEquivalence()
    parts = ["# Censoring Observation Equivalence V3 - samples (P003v3)"]
    for level in (0, 2, 5):
        xs = gen(task, level)
        parts.append(f"\n## Level {level}")
        parts.append(
            f"Config: n={task.config.length}, maxval={task.config.maxval}, "
            f"blocks={task.config.blocks}\n"
        )
        for i, x in enumerate(xs, 1):
            parts.append(f"### Example {i}")
            parts.append("**Prompt:**")
            parts.append(x.prompt)
            parts.append("")
            parts.append(f"**Answer:** {x.answer}")
            parts.append("")
    OUT.write_text("\n".join(parts))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
