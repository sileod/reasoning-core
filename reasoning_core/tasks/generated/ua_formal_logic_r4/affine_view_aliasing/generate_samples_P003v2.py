import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.affine_view_aliasing.affine_view_aliasing import (
    AffineViewAliasing,
)

random.seed(382564971)


def main():
    task = AffineViewAliasing()
    out = Path(__file__).with_name("samples_P003v2.md")
    lines = []
    lines.append("# samples_P003v2 — affine_view_aliasing")
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
