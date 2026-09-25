import random
from pathlib import Path

random.seed(2701974858)

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.finite_partizan_order.finite_partizan_order import (
    FinitePartizanOrder,
)


def main():
    task = FinitePartizanOrder()
    out = Path(__file__).with_name("samples_P009v2.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d" % level)
        lines.append("")
        for i in range(2):
            ex = task.generate_example()
            lines.append("### Example %d" % (i + 1))
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines))
    print("wrote %s" % out)


if __name__ == "__main__":
    main()
