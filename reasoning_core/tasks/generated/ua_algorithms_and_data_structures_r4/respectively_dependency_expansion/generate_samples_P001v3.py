import random
from pathlib import Path

random.seed(4238614268)

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.respectively_dependency_expansion.respectively_dependency_expansion import (
    RespectivelyDependencyExpansion,
)


def main():
    task = RespectivelyDependencyExpansion()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"# Level {level}")
        for _ in range(2):
            entry = task.generate_example()
            out.append("")
            out.append("**Prompt:**")
            out.append(entry.prompt)
            out.append("")
            out.append("**Answer:**")
            out.append(entry.answer)
            out.append("")

    path = Path(__file__).with_name("samples_P001v3.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
