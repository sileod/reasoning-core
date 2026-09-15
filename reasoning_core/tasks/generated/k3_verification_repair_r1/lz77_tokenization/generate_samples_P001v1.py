import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.lz77_tokenization.lz77_tokenization import (
    LZ77Tokenization,
)

random.seed(1662004003)

task = LZ77Tokenization()
out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append("## Level %d\n" % level)
    for _ in range(2):
        ex = task.generate_example()
        out.append("**Prompt:**\n\n" + ex.metadata["_prompt"] if False else "")
        out.append("**Prompt:**\n\n%s" % task.render_prompt(ex.metadata))
        out.append("\n**Answer:**\n\n%s\n" % ex.answer)

Path(__file__).with_name("samples_P001v1.md").write_text("\n".join(out) + "\n")
