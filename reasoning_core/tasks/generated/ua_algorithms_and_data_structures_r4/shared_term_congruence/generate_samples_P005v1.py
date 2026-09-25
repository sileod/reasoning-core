import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.shared_term_congruence.shared_term_congruence import (
    SharedTermCongruence,
)

random.seed(729651269)


def main():
    task = SharedTermCongruence()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            lines.append("### Example")
            lines.append("**Prompt:**")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append(ex.answer)
            lines.append("")
    out = Path(__file__).with_name("samples_P005v1.md")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
