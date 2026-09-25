import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_relational_structures_r4.interval_doubled_posets.interval_doubled_posets import (
    IntervalDoubledPosets,
)

SEED = 2701974858
LEVELS = (0, 2, 5)
EXAMPLES_PER_LEVEL = 2

TASK = IntervalDoubledPosets()


def main():
    random.seed(SEED)
    lines = []
    lines.append("# Samples for interval_doubled_posets (P009v2)")
    lines.append("")
    for level in LEVELS:
        TASK.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for idx in range(EXAMPLES_PER_LEVEL):
            e = TASK.generate_example()
            lines.append(f"### Example {idx + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(TASK.render_prompt(e.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(e.answer)
            lines.append("")
    out = Path(__file__).with_name("samples_P009v2.md")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
