import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.chromatid_segment_ancestry.chromatid_segment_ancestry import (
    ChromatidSegmentAncestry,
)

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")
LEVELS = (0, 2, 5)

task = ChromatidSegmentAncestry()

with OUT.open("w") as f:
    f.write("# samples_P003v1\n\n")
    f.write("Query a chromatid's full ordered haplotype (0/1 string) after "
            "reciprocal crossovers and directed gene-conversion tracts.\n\n")
    for level in LEVELS:
        task.config.set_level(level)
        f.write(f"## Level {level}\n\n")
        for i in range(2):
            x = task.generate_example()
            f.write(f"### Example {i + 1}\n\n")
            f.write(f"**Prompt:**\n\n{x.prompt}\n\n")
            f.write(f"**Answer:** {x.answer}\n\n")

print(f"wrote {OUT}")
