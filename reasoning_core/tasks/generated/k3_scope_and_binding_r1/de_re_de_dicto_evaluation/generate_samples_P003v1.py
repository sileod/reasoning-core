import random
from pathlib import Path

from de_re_de_dicto_evaluation import DeReDeDictoEvaluation

random.seed(2267388306)

OUT = Path(__file__).with_name("samples_P003v1.md")
task = DeReDeDictoEvaluation()

blocks = []
for level in (0, 2, 5):
    blocks.append(f"Level {level}")
    for _ in range(2):
        entry = task.generate_example(level=level, timeout=60)
        blocks.append("Prompt:\n" + entry.prompt)
        blocks.append("Answer: " + entry.answer)

OUT.write_text("\n\n".join(blocks) + "\n")
print("wrote", OUT)
