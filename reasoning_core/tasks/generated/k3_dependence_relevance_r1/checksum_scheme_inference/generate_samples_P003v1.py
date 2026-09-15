import random
from pathlib import Path

random.seed(2267388306)

MODULE = "reasoning_core.tasks.generated.k3_dependence_relevance_r1.checksum_scheme_inference.checksum_scheme_inference"
import importlib

m = importlib.import_module(MODULE)

task = m.ChecksumSchemeInference()

out = []
for lvl in (0, 2, 5):
    task.config.set_level(lvl)
    out.append(f"## Level {lvl}\n")
    for i in range(2):
        e = task.generate_example()
        out.append(f"### Example {i+1}\n")
        out.append("**Prompt:**\n")
        out.append(task.render_prompt(e.metadata) + "\n")
        out.append("**Answer:**\n")
        out.append(e.answer + "\n")
    out.append("")

(text := "\n".join(out))
output = Path(__file__).with_name("samples_P003v1.md")
output.write_text(text)
print(text)
