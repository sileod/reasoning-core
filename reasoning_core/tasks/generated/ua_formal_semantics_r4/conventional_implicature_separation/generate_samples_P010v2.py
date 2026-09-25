import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_semantics_r4.conventional_implicature_separation.conventional_implicature_separation import (
    ConventionalImplicatureSeparation,
)

SEED = 1211525277
OUT = Path(__file__).with_name("samples_P010v2.md")


def main():
    random.seed(SEED)
    task = ConventionalImplicatureSeparation()
    lines = ["# Samples for conventional_implicature_separation (P010v2)", ""]
    for level, count in ((0, 2), (2, 2), (5, 2)):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(count):
            x = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt**")
            lines.append("")
            lines.append(task.render_prompt(x.metadata))
            lines.append("")
            lines.append("**Answer**")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
