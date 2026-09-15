"""Generate samples_P001v1.md for the distributed snapshot recording task."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_representation_transfer_r1.distributed_snapshot_recording.distributed_snapshot_recording import (  # noqa: E501
    DistributedSnapshotRecording,
)

SEED = 1662004003


def main():
    random.seed(SEED)
    out = Path(__file__).with_name("samples_P001v1.md")
    task = DistributedSnapshotRecording()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        task.config.set_level(level)
        for i in range(2):
            entry = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("**Prompt:**")
            lines.append(task.render_prompt(entry.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append(entry.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
