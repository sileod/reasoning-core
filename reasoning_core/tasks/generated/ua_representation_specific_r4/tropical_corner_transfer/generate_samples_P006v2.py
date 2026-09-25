import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_specific_r4.tropical_corner_transfer.tropical_corner_transfer import (
    TropicalCornerTransfer,
)

SEED = 1705404348


def main():
    random.seed(SEED)
    task = TropicalCornerTransfer()
    out = Path(__file__).with_name("samples_P006v2.md")
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example(level=level)
            lines.append(ex.prompt)
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
