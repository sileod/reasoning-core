import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_rule_induction_r1.smith_normal_form.smith_normal_form import (
    SmithNormalForm,
)

random.seed(1475571465)


def main():
    out = Path(__file__).with_name("samples_P002v1.md")
    task = SmithNormalForm()
    lines = ["# Smith Normal Form samples (P002v1)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            x = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(x.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(x.answer)
            lines.append("")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
