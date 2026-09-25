import random

from pathlib import Path

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.ribbon_surface_surgery.ribbon_surface_surgery import (
    RibbonSurfaceSurgery,
)

random.seed(2305351643)


def main():
    out = Path(__file__).with_name("samples_P011v1.md")
    task = RibbonSurfaceSurgery()
    lines = []
    lines.append("# P011v1 ribbon_surface_surgery samples")
    lines.append("")
    for lvl in (0, 2, 5):
        task.config.set_level(lvl)
        lines.append(f"## Level {lvl}")
        lines.append("")
        for _ in range(2):
            e = task.generate_example()
            prompt = task.render_prompt(e.metadata)
            lines.append("### Prompt")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append("```")
            lines.append(e.answer)
            lines.append("```")
            lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
