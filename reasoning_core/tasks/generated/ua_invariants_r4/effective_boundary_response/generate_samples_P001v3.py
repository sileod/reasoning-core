import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_invariants_r4.effective_boundary_response.effective_boundary_response import (
    EffectiveBoundaryResponse,
)

random.seed(4238614268)

OUT = Path(__file__).with_name("samples_P001v3.md")


def main():
    task = EffectiveBoundaryResponse()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example(level=level)
            lines.append(f"### Example {i+1} (mode {ex.metadata['mode']})")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"`{ex.answer}`")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
