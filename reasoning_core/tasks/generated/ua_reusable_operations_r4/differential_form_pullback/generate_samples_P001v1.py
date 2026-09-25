import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_reusable_operations_r4.differential_form_pullback.differential_form_pullback import (
    DifferentialFormPullback,
)

SEED = 1662004003


def main():
    random.seed(SEED)
    task = DifferentialFormPullback()
    lines = []
    for lvl in (0, 2, 5):
        task.config.set_level(lvl)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"## Level {lvl}\n")
            lines.append(f"### Example {i + 1}\n")
            lines.append("**Prompt**\n")
            lines.append(ex.prompt)
            lines.append("\n**Answer**\n")
            lines.append(str(ex.answer))
            lines.append("\n")
    out = Path(__file__).with_name("samples_P001v1.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
