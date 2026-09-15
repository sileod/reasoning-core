import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_uncertainty_r1.kripke_knowledge_evaluation.kripke_knowledge_evaluation import (
    KripkeKnowledgeEvaluation,
)

random.seed(1475571465)

task = KripkeKnowledgeEvaluation()

lines = []
for level in (0, 2, 5):
    lines.append(f"## Level {level}")
    task.config.set_level(level)
    for i in range(2):
        ex = task.generate_example()
        lines.append(f"### Example {i + 1}")
        lines.append("**Prompt**")
        lines.append(ex.prompt)
        lines.append("")
        lines.append("**Answer**")
        lines.append(ex.answer)
        lines.append("")

out = Path(__file__).with_name("samples_P002v1.md")
out.write_text("\n".join(lines))
