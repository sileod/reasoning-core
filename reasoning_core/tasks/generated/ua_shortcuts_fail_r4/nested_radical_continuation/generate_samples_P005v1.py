import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_shortcuts_fail_r4.nested_radical_continuation import (
    nested_radical_continuation as m,
)

random.seed(729651269)

OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    task = m.NestedRadicalContinuation()
    lines = []
    for level, count in ((0, 2), (2, 2), (5, 2)):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(count):
            task.config.set_level(level)
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append("**Prompt:**")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
