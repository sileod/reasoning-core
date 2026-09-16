import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_synthetic_grammars_r1.aspectual_class_entailment.aspectual_class_entailment import (
    AspectualClassEntailment,
)

random.seed(1662004003)

OUT = Path(__file__).with_name("samples_P001v1.md")
task = AspectualClassEntailment()


def write_example(f, level):
    task.config.set_level(level)
    ex = task.generate_example()
    f.write("Prompt:\n")
    f.write(task.render_prompt(ex.metadata) + "\n")
    f.write("\nAnswer:\n")
    f.write(ex.answer + "\n\n")


with open(OUT, "w") as f:
    for level in (0, 2, 5):
        f.write(f"## Level {level}\n\n")
        for _ in range(2):
            write_example(f, level)

print(f"wrote {OUT}")
