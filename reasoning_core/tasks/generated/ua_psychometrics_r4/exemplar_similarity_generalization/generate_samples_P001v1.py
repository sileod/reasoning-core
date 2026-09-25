import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_psychometrics_r4.exemplar_similarity_generalization.exemplar_similarity_generalization import (
    ExemplarSimilarityGeneralization,
)

random.seed(1662004003)
task = ExemplarSimilarityGeneralization()

out = Path(__file__).with_name("samples_P001v1.md")
with open(out, "w") as f:
    for level in (0, 2, 5):
        f.write(f"## Level {level}\n\n")
        for i in range(2):
            x = task.generate_example(level=level)
            f.write(f"**Example {i+1}**\n\n")
            f.write(f"Prompt:\n```\n{x.prompt}\n```\n\n")
            f.write(f"Answer:\n```\n{x.answer}\n```\n\n")
