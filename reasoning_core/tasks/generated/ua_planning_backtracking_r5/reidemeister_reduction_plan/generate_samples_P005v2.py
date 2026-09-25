import os
os.environ.setdefault('PYTHONHASHSEED', '0')

import random
random.seed(2072234021)

from pathlib import Path

from reasoning_core.template import Task

from reidemeister_reduction_plan import (
    ReidemeisterReductionPlan,
    _bar,
    _canon,
    _min_reduce,
)


def _run():
    task = ReidemeisterReductionPlan()
    out = Path(__file__).with_name("samples_P005v2.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        for idx in range(2):
            e = task.generate_example()
            lines.append("### Example %d" % (idx + 1))
            lines.append("**Prompt**")
            lines.append(task.render_prompt(e.metadata))
            lines.append("**Answer**")
            lines.append(e.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    _run()
