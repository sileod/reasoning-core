import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.dyadic_balance_patch.dyadic_balance_patch import (
    DyadicBalancePatch,
)

SEED = 3867019559
OUT = Path(__file__).with_name("samples_P009v1.md")


def main():
    random.seed(SEED)
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            task = DyadicBalancePatch()
            task.config.set_level(level)
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {ex.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
