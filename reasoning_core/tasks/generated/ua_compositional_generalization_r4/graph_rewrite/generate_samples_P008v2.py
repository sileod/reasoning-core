import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.graph_rewriting_system.graph_rewriting_system import (
    GraphRewriteV2,
)

random.seed(3020341981)

out = Path(__file__).with_name("samples_P008v2.md")
with open(out, "w") as f:
    for level, heading in [(0, "Level 0"), (2, "Level 2"), (5, "Level 5")]:
        f.write(f"## {heading}\n\n")
        for ex in range(2):
            t = GraphRewriteV2()
            t.config.set_level(level)
            ex = t.generate_example()
            f.write("### Example\n\n")
            f.write("**Prompt:**\n\n")
            f.write("\n\n".join(line for line in ex.prompt.split("\n")) + "\n\n")
            f.write("**Answer:**\n\n")
            f.write(ex.answer + "\n\n")
            f.write("---\n\n")
