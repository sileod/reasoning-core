import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_verification_repair_r4.sumcheck_transcript_audit.sumcheck_transcript_audit import (
    SumcheckTranscriptAudit,
)

SEED = 1336314872
LEVELS = [0, 2, 5]
NEXT = [0, 1, 0, 1, 0, 1]

random.seed(SEED)

task = SumcheckTranscriptAudit()

chunks = []
for level in LEVELS:
    cfg = task.config_cls()
    cfg.set_level(level)
    task.config = cfg
    chunks.append(f"## Level {level}")
    for k in range(2):
        x = task.generate_example()
        chunks.append(f"### Example {k + 1}")
        chunks.append("**Prompt:**")
        chunks.append("```")
        chunks.append(task.render_prompt(x.metadata))
        chunks.append("```")
        chunks.append("**Answer:**")
        chunks.append("```")
        chunks.append(x.answer)
        chunks.append("```")
        random.seed(SEED + level * 10 + k)  # keep reproducibility contained

out = Path(__file__).with_name("samples_P002v2.md")
out.write_text("\n".join(chunks) + "\n")
print("wrote", out)
