import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.minesweeper_definite_cells.minesweeper_definite_cells import (
    MinesweeperDefiniteCells,
)

random.seed(2267388306)

task = MinesweeperDefiniteCells()
out = []
for level in (0, 2, 5):
    out.append("## Level %d" % level)
    for i in range(2):
        ex = task.generate_example(level=level)
        out.append("### Example %d" % (i + 1))
        out.append("Prompt:")
        out.append(ex.prompt)
        out.append("Answer: %s" % ex.answer)
        out.append("")

Path(__file__).with_name("samples_P003v1.md").write_text("\n".join(out))
print("wrote samples_P003v1.md")
