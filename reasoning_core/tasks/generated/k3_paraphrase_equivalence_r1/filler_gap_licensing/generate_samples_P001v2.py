import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r1.filler_gap_licensing.filler_gap_licensing import (
    FillerGapLicensingV2Config,
    FillerGapLicensingV2Task,
)

random.seed(2302342651)

OUT = Path(__file__).with_name("samples_P001v2.md")

task = FillerGapLicensingV2Task()

lines = []
lines.append("# Samples for P001v2 (filler_gap_licensing)")
lines.append("")

for level in (0, 2, 5):
    cfg = FillerGapLicensingV2Config()
    cfg.set_level(level)
    task.config = cfg
    lines.append("## Level %d" % level)
    lines.append("")
    for _ in range(2):
        ex = task.generate_example()
        lines.append("**Prompt:** " + task.render_prompt(ex.metadata))
        lines.append("")
        lines.append("**Answer:** " + ex.answer)
        lines.append("")

OUT.write_text("\n".join(lines))
print("wrote", OUT)
