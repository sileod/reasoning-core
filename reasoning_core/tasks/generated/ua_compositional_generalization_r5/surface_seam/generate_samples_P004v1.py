import random

from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r5.surface_seam_composition.surface_seam_composition import (
    SurfaceSeamV1,
)


def main():
    random.seed(3536382515)
    task = SurfaceSeamV1()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for _ in range(2):
            ex = task.generate_example()
            lines.append(task.render_prompt(ex.metadata))
            lines.append("Answer: " + ex.answer)
            lines.append("")
        lines.append("")
    out = Path(__file__).with_name("samples_P004v1.md")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
