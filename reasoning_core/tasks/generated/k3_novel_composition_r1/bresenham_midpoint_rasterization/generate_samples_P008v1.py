import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_novel_composition_r1.bresenham_midpoint_rasterization.bresenham_midpoint_rasterization import (
    BresenhamMidpointRasterization,
)

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(682015719)
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}\n")
        task = BresenhamMidpointRasterization()
        task.config.set_level(level)
        for _ in range(LEVELS[level]):
            entry = task.generate_example()
            out.append("**Prompt:**")
            prompt_text = task.render_prompt(entry.metadata)
            out.append("```\n" + prompt_text + "\n```")
            out.append("**Answer:**")
            out.append("```\n" + entry.answer + "\n```")
            out.append("")
    dest = Path(__file__).with_name("samples_P008v1.md")
    dest.write_text("\n".join(out))


if __name__ == "__main__":
    main()
