import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_operations_research_r4.tiered_price_lot_clipping.tiered_price_lot_clipping import (
    TieredPriceLotClipping,
)

random.seed(3867019559)

OUT = Path(__file__).with_name("samples_P009v1.md")

task = TieredPriceLotClipping()


def run_level(level, n):
    task.config.set_level(level)
    rows = []
    for _ in range(n):
        ex = task.generate_example()
        rows.append((task.render_prompt(ex.metadata), ex.answer))
    return rows


with open(OUT, "w") as f:
    f.write("# Samples for tiered_price_lot_clipping (P009v1)\n\n")
    for level, n in ((0, 2), (2, 2), (5, 2)):
        f.write(f"## Level {level}\n\n")
        rows = run_level(level, n)
        for prompt, answer in rows:
            f.write(prompt + "\n\n")
            f.write("Answer: " + answer + "\n\n")
