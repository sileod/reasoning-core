import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dynamic_structures_r5.liquidity_range_updates.liquidity_range_updates import (
    LiquidityRangeUpdates,
)

random.seed(1259343118)

task = LiquidityRangeUpdates()

out = []
for level in (0, 2, 5):
    out.append("## Level %d" % level)
    for _ in range(2):
        ex = task.generate_example(level=level)
        out.append("")
        out.append("### Prompt")
        out.append("```")
        out.append(ex.prompt)
        out.append("```")
        out.append("")
        out.append("Answer: %s" % ex.answer)
    out.append("")

Path(__file__).with_name("samples_P003v3.md").write_text("\n".join(out) + "\n")
