import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_specific_r1.necklace_canonical_rotation.necklace_canonical_rotation import (
    NecklaceCanonicalRotation,
)

SEED = 3867019559


def main():
    random.seed(SEED)
    task = NecklaceCanonicalRotation()
    out = Path(__file__).with_name("samples_P009v1.md")
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
