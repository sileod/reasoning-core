import random
from pathlib import Path

random.seed(2267388306)

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.graph_local_complementation.task_graph_local_complementation import (
    GraphLocalComplementV1,
)


def main():
    task = GraphLocalComplementV1()
    out = Path(__file__).with_name("samples_P003v1.md")
    lines = ["# samples_P003v1", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            task.config.set_level(level)
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            lines.append(prompt)
            lines.append("")
            lines.append(f"Answer: {x.answer}")
            lines.append("")
    out.write_text("\n".join(lines))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
