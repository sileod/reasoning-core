import random
from pathlib import Path

from reasoning_core.template import Task

from pairwise_majority_smith_set import SmithSetTask

SEED = 2267388306
OUT = Path(__file__).with_name("samples_P003v1.md")


def main():
    random.seed(SEED)
    task = SmithSetTask()
    lines = ["# Samples P003v1", ""]
    for lvl in (0, 2, 5):
        lines.append(f"## Level {lvl}")
        lines.append("")
        task.config.set_level(lvl)
        for k in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {k + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            for pl in task.render_prompt(ex.metadata).split("\n"):
                lines.append(f"> {pl}")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"`{ex.answer}`")
            lines.append("")
        lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
