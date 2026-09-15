import random
from pathlib import Path

from reasoning_core.template import Entry
from reasoning_core.tasks.generated.k3_representation_transfer_r1.floor_quotient_blocks.floor_quotient_blocks import (
    FloorQuotientBlocks,
    FloorQuotientBlocksConfig,
)


def main():
    random.seed(2072234021)
    out = []
    for level in (0, 2, 5):
        task = FloorQuotientBlocks(config=FloorQuotientBlocksConfig())
        task.config.set_level(level)
        out.append(f"## Level {level}")
        for _ in range(2):
            ex = task.generate_example(level=level)
            out.append("### Prompt")
            out.append(ex.prompt)
            out.append("### Answer")
            out.append(ex.answer)
            out.append("")
    Path(__file__).with_name("samples_P005v2.md").write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
