import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relational_structures_r1.symbolic_differentiation.symbolic_differentiation import (
    SymbolicDifferentiation,
)

SEED = 1336314872


def main():
    random.seed(SEED)
    task = SymbolicDifferentiation()
    out = Path(__file__).with_name("samples_P002v2.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}\n")
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i+1}\n")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("\n")
            lines.append(f"Answer: {ex.answer}\n")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
