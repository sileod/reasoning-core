import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_invariants_r1.perceptron_update_trace.perceptron_update_trace import (
    PerceptronUpdateTrace,
)

SEED = 1705404348
OUT = Path(__file__).with_name("samples_P006v2.md")

random.seed(SEED)


def main():
    task = PerceptronUpdateTrace()
    lines = []
    lines.append("# Perceptron update trace (P006v2) samples")
    lines.append("")
    lines.append("Fixed seed %d; two examples per requested level." % SEED)
    lines.append("")
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d" % level)
        lines.append("")
        for k in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            lines.append("### Example %d" % (k + 1))
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            for pl in prompt.split("\n"):
                lines.append("    " + pl)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append("    " + ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
