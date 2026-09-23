import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_non_local_structured_r4.fluent_persistence_windows.fluent_persistence_windows import (
    FluentPersistenceWindows,
)


def main():
    random.seed(2267388306)
    out = []
    task = FluentPersistenceWindows()
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        out.append("")
        for i in range(1, 3):
            task.config.set_level(level)
            ex = task.generate_example()
            out.append(f"### Example {i}")
            out.append("")
            out.append("**Prompt:**")
            out.append("")
            out.append(ex.prompt)
            out.append("")
            out.append("**Answer:**")
            out.append("")
            out.append(ex.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P003v1.md")
    path.write_text("\n".join(out) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
