import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_interacting_updates_r5.binary_matrix_margin_realization.binary_matrix_margin_realization import (
    BinaryMatrixMarginRealization,
)


def main():
    random.seed(1662004003)
    out = Path(__file__).with_name("samples_P001v1.md")
    task = BinaryMatrixMarginRealization()
    lines = []
    lines.append("# samples_P001v1")
    lines.append("")
    for lvl in (0, 2, 5):
        cfg = task.config_cls()
        cfg.set_level(lvl)
        task.config = cfg
        lines.append(f"## Level {lvl}")
        lines.append("")
        for k in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {k+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(ex.metadata.get("_prompt", task.render_prompt(ex.metadata)))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    out.write_text("\n".join(lines))
    print(out)


if __name__ == "__main__":
    main()
