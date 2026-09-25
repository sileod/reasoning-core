import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_interacting_updates_r5.substitution_uniform_recurrence.substitution_uniform_recurrence import (
    SubstitutionUniformRecurrence,
)

random.seed(1475571465)


def main():
    out = Path(__file__).with_name("samples_P002v1.md")
    task = SubstitutionUniformRecurrence()
    buf = []
    for level in (0, 2, 5):
        buf.append(f"# Level {level}")
        buf.append("")
        task.config.set_level(level)
        for i in range(2):
            x = task.generate_example()
            prompt = task.render_prompt(x.metadata)
            buf.append(f"### Example {i + 1}")
            buf.append("")
            buf.append("**Prompt:**")
            buf.append("")
            buf.append(prompt)
            buf.append("")
            buf.append("**Answer:**")
            buf.append("")
            buf.append(x.answer)
            buf.append("")
    out.write_text("\n".join(buf), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
