import random
from pathlib import Path

random.seed(4238614268)

from reasoning_core.tasks.generated.k3_novel_composition_r1.session_type_projection.session_type_projection import (
    SessionTypeProjection,
)


def main():
    task = SessionTypeProjection()
    out = []
    out.append("# Samples: session_type_projection (P001v3)")
    out.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}")
        out.append("")
        for i in range(2):
            ex = task.generate_example()
            out.append(f"### Example {i + 1}")
            out.append("")
            out.append("**Prompt**")
            out.append("")
            out.append(task.render_prompt(ex.metadata))
            out.append("")
            out.append("**Answer**")
            out.append("")
            out.append(ex.answer)
            out.append("")
    text = "\n".join(out)
    target = Path(__file__).with_name("samples_P001v3.md")
    target.write_text(text)
    print(target)


if __name__ == "__main__":
    main()
