import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dynamic_structures_r5.tree_pair_group_product.tree_pair_group_product import (
    TreePairGroupProduct,
)

random.seed(1662004003)

OUT = Path(__file__).with_name("samples_P001v1.md")

task = TreePairGroupProduct()

lines = []


def emit(level):
    task.config.set_level(level)
    lines.append(f"## Level {level}")
    for i in range(2):
        ex = task.generate_example()
        lines.append("### Example %d" % (i + 1))
        lines.append("Prompt:")
        lines.append(ex.prompt)
        lines.append("Answer:")
        lines.append(ex.answer)


for lvl in (0, 2, 5):
    emit(lvl)

OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(OUT)
