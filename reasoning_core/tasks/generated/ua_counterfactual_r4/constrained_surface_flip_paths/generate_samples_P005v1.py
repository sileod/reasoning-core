import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_counterfactual_r4.constrained_surface_flip_paths.constrained_surface_flip_paths import (
    ConstrainedSurfaceFlipPaths,
)

SEED = 729651269
OUT = Path(__file__).with_name("samples_P005v1.md")


def main():
    random.seed(SEED)
    task = ConstrainedSurfaceFlipPaths()
    lines = [
        "# Samples: constrained_surface_flip_paths (P005v1)",
        "",
    ]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for idx in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append(f"### Example {idx + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            for pl in prompt.split("\n"):
                lines.append(f"> {pl}")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"> {x.answer}")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
