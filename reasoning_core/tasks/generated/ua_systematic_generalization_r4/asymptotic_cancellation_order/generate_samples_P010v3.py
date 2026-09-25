import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_systematic_generalization_r4.asymptotic_cancellation_order.asymptotic_cancellation_order import (
    AsymptoticCancellationOrder,
)


def main():
    seed = 3143501959
    random.seed(seed)
    task = AsymptoticCancellationOrder()
    out = Path(__file__).with_name("samples_P010v3.md")
    blocks = []
    for level in (0, 2, 5):
        lines = [f"# Level {level}", ""]
        for i in range(2):
            task.config.set_level(level)
            ex = task.generate_example()
            lines.append(f"## Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
        blocks.append("\n".join(lines))
    out.write_text("\n\n".join(blocks), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
