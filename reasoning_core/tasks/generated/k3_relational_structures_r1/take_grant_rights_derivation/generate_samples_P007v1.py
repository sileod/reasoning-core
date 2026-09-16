import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_relational_structures_r1.take_grant_rights_derivation.take_grant_rights_derivation import (
    TakeGrantRightsDerivation,
)

OUT = Path(__file__).with_name("samples_P007v1.md")

random.seed(1139467751)


def main():
    task = TakeGrantRightsDerivation()
    lines = []
    for level in (0, 2, 5):
        lines.append("## Level %d" % level)
        for _ in range(2):
            e = task.generate_example(level=level)
            prompt = task.render_prompt(e.metadata)
            lines.append("### Prompt")
            lines.append(prompt)
            lines.append("### Answer")
            lines.append(e.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
