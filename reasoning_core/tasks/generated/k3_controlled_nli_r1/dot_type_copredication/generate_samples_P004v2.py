import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.dot_type_copredication.dot_type_copredication import (
    DotTypeCopredication,
)


def main():
    random.seed(3577985643)
    task = DotTypeCopredication()
    out = []
    for level in [0, 2, 5]:
        task.config.set_level(level)
        for _ in range(2):
            entry = task.generate_example()
            out.append(f"## Level {level}\n")
            out.append(task.render_prompt(entry.metadata))
            out.append(f"\nAnswer: {entry.answer}\n")
    path = Path(__file__).with_name("samples_P004v2.md")
    path.write_text("\n".join(out), encoding="utf-8")


if __name__ == "__main__":
    main()
