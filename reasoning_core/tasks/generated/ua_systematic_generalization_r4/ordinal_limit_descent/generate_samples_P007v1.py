import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.ordinal_limit_descent.ordinal_limit_descent import (
    OrdinalLimitDescent,
)

random.seed(1139467751)

OUT = Path(__file__).with_name("samples_P007v1.md")

if __name__ == "__main__":
    task = OrdinalLimitDescent()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(1, 3):
            ex = task.generate_example(level=level)
            lines.append(f"### Example {i}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print("wrote", OUT)
