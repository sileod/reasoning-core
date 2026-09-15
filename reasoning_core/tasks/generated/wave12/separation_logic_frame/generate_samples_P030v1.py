import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.separation_logic_frame.separation_logic_frame import (
    SeparationLogicFrame,
)


def main():
    random.seed(1990082874)
    task = SeparationLogicFrame()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}")
        for i in range(2):
            ex = task.generate_example()
            out.append("### Example %d" % (i + 1))
            out.append("Prompt:")
            out.append(task.render_prompt(ex.metadata))
            out.append("")
            out.append("Answer:")
            out.append(ex.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P030v1.md")
    path.write_text("\n".join(out) + "\n")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
