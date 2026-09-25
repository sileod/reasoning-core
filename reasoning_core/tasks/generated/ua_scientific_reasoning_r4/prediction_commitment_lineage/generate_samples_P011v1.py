import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.prediction_commitment_lineage.prediction_commitment_lineage import (
    PredictionCommitmentLineage,
)

random.seed(2305351643)

task = PredictionCommitmentLineage()
out = Path(__file__).with_name("samples_P011v1.md")
lines = ["# Samples for P011v1 (prediction_commitment_lineage)", ""]
for level in (0, 2, 5):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    lines.append("")
    for i in range(2):
        e = task.generate_example()
        lines.append(f"### Example {i+1}")
        lines.append("Prompt:")
        lines.append(task.render_prompt(e.metadata))
        lines.append("")
        lines.append("Answer:")
        lines.append(e.answer)
        lines.append("")
        lines.append("---")
        lines.append("")
out.write_text("\n".join(lines))
print(out)
