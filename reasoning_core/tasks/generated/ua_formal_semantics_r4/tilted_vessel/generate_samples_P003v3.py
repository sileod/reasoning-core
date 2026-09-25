import random
from pathlib import Path

from reasoning_core.template import Task

random.seed(1259343118)

from reasoning_core.tasks.generated.ua_formal_semantics_r4.tilted_vessel_spillage.tilted_vessel_spillage import TiltedVessel

OUT = Path(__file__).with_name("samples_P003v3.md")


def main():
    task = TiltedVessel()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        for _ in range(2):
            ex = task.generate_example()
            lines.append("## Level %d" % level)
            lines.append("")
            lines.append("### Prompt")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
