import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_representation_specific_r4.multivalued_dependency_closure.multivalued_dependency_closure import (
    MultivaluedDependencyClosure,
)

SEED = 682015719
OUT = Path(__file__).with_name("samples_P008v1.md")


def main():
    random.seed(SEED)
    task = MultivaluedDependencyClosure()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for i in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append(f"### Example {i + 1}")
            lines.append("Prompt:")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
