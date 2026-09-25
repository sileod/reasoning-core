import random
from pathlib import Path

random.seed(1705404348)

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.dormant_independence_testing.dormant_independence_testing import (
    DormantIndependenceTesting,
)

OUT = Path(__file__).with_name("samples_P006v2.md")


def render_levels():
    lines = []
    for level in (0, 2, 5):
        task = DormantIndependenceTesting()
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("**Prompt**")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("**Answer**")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    OUT.write_text(render_levels() + "\n")
    print(OUT)
