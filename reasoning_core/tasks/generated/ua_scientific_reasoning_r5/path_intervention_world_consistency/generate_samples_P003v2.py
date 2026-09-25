import random
from pathlib import Path

random.seed(382564971)

from reasoning_core.tasks.generated.ua_scientific_reasoning_r5.path_intervention_world_consistency.path_intervention_world_consistency import (
    PathInterventionWorldConsistency,
)

OUT = Path(__file__).with_name("samples_P003v2.md")


def render_levels():
    lines = []
    for level in (0, 2, 5):
        task = PathInterventionWorldConsistency()
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        seen = set()
        i = 0
        while len(seen) < 2:
            ex = task.generate_example()
            if ex.answer not in seen:
                seen.add(ex.answer)
            else:
                continue
            i += 1
            lines.append(f"### Example {i}")
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
