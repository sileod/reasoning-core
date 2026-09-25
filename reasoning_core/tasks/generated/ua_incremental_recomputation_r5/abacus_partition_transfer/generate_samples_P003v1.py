import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r5.abacus_partition_transfer.abacus_partition_transfer import (
    AbacusPartitionTransfer,
)


def main():
    random.seed(2267388306)
    task = AbacusPartitionTransfer()
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        out.append("")
        for i in range(2):
            ex = task.generate_example(level=level)
            out.append(f"### Example {i + 1}")
            out.append("")
            out.append("**Prompt:**")
            out.append("")
            out.append(ex.prompt)
            out.append("")
            out.append(f"**Answer:** {ex.answer}")
            out.append("")
    path = Path(__file__).with_name("samples_P003v1.md")
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
