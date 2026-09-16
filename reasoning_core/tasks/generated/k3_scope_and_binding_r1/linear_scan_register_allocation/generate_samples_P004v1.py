import random
from pathlib import Path

from reasoning_core.template import Config
from linear_scan_register_allocation import (
    LinearScanRegisterAllocation,
    LinearScanRegisterAllocationConfig,
)

random.seed(3536382515)

task = LinearScanRegisterAllocation()

lines = []
for level in (0, 2, 5):
    lines.append(f"# Level {level}")
    for _ in range(2):
        cfg = LinearScanRegisterAllocationConfig()
        cfg.set_level(level)
        task.config = cfg
        ex = task.generate_example()
        lines.append("## Prompt")
        lines.append(task.render_prompt(ex.metadata))
        lines.append("## Answer")
        lines.append(ex.answer)
        lines.append("")

out = Path(__file__).with_name("samples_P004v1.md")
out.write_text("\n".join(lines) + "\n")
