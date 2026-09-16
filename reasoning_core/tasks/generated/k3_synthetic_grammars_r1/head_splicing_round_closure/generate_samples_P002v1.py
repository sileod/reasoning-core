import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.head_splicing_round_closure.head_splicing_round_closure import (
    HeadSplicingRoundClosure,
)

SEED = 1475571465
OUT = Path(__file__).with_name("samples_P002v1.md")


def main():
    random.seed(SEED)
    task = HeadSplicingRoundClosure()
    lines = ["# Samples for head_splicing_round_closure (P002v1)",
             "Trial seed: 1475571465", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            ex = task.generate_example()
            lines.append("### Prompt")
            lines.append("")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
