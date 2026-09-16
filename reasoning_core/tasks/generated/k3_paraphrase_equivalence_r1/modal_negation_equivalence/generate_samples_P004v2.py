import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_paraphrase_equivalence_r1.modal_negation_equivalence.modal_negation_equivalence import (
    ModalNegationEquivalence,
)

random.seed(3577985643)

task = ModalNegationEquivalence()
out = []
for level in (0, 2, 5):
    task.config.set_level(level)
    out.append(f"## Level {level}\n")
    for i in range(2):
        ex = task.generate_example()
        prompt = task.render_prompt(ex.metadata)
        out.append(f"### Example {i+1}\n")
        out.append(f"**Prompt:**\n\n{prompt}\n")
        out.append(f"\n**Answer:**\n\n{ex.answer}\n")

Path(__file__).with_name("samples_P004v2.md").write_text("\n".join(out))
