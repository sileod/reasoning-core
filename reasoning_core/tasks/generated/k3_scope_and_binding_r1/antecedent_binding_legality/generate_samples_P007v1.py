"""Generate the samples file for antecedent_binding_legality."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.antecedent_binding_legality.antecedent_binding_legality import (
    AntecedentBindingLegality,
)

SEED = 1139467751


def main():
    random.seed(SEED)
    task = AntecedentBindingLegality()
    out = Path(__file__).with_name("samples_P007v1.md")
    parts = [
        "# samples_P007v1 - antecedent_binding_legality",
        "",
    ]
    for level in (0, 2, 5):
        parts.append(f"## Level {level}")
        parts.append("")
        task.config.set_level(level)
        for k in range(2):
            x = task.generate_example(level=level)
            parts.append(f"### Example {k + 1}")
            parts.append("")
            parts.append("**Prompt:**")
            parts.append("")
            parts.append(task.render_prompt(x.metadata))
            parts.append("")
            parts.append("**Answer:**")
            parts.append("")
            parts.append(f"`{x.answer}`")
            parts.append("")
    out.write_text("\n".join(parts))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
