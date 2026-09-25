import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.unilateral_contact_equilibrium.unilateral_contact_equilibrium import (
    UnilateralContactEquilibrium,
)


def main():
    random.seed(1140349348)
    task = UnilateralContactEquilibrium()

    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append("# Level %d" % level)
        for i in range(2):
            entry = task.generate_example()
            out.append("## Example %d" % (i + 1))
            out.append(entry.prompt)
            out.append("")
            out.append("Answer: %s" % entry.answer)
            out.append("")

    path = Path(__file__).with_name("samples_P005v3.md")
    path.write_text("\n".join(out) + "\n")
    print("wrote", path)


if __name__ == "__main__":
    main()
