import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_specific_r4.observed_remove_delta_merge.observed_remove_delta_merge import (
    ObservedRemoveDeltaMerge,
)

random.seed(2267388306)


def main():
    task = ObservedRemoveDeltaMerge()
    out = Path(__file__).with_name("samples_P003v1.md")
    parts = []
    parts.append("# samples_P003v1")
    parts.append("")
    for level in (0, 2, 5):
        parts.append(f"## Level {level}")
        parts.append("")
        task.config.set_level(level)
        for i in range(2):
            x = task.generate_example()
            parts.append(f"### Example {i+1}")
            parts.append("")
            parts.append("Prompt:")
            parts.append("")
            parts.append("```")
            parts.append(task.render_prompt(x.metadata))
            parts.append("```")
            parts.append("")
            parts.append("Answer:")
            parts.append("")
            parts.append("```")
            parts.append(x.answer)
            parts.append("```")
            parts.append("")
    out.write_text("\n".join(parts))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
