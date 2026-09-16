import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_hierarchical_recursive_r1.extensive_form_to_bimatrix.extensive_form_to_bimatrix import (
    ExtensiveFormToBimatrix,
)

SEED = 368817805
OUT = Path(__file__).with_name("samples_P002v3.md")


def main():
    random.seed(SEED)
    task = ExtensiveFormToBimatrix()
    lines = ["# Samples for extensive_form_to_bimatrix (P002v3)\n"]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}\n")
        cfg = task.config_cls()
        cfg.apply_difficulty(level)
        task.config = cfg
        for _ in range(2):
            e = task.generate_entry()
            prompt = task.render_prompt(e.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {e.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
