import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_verification_repair_r1.simplex_pivot_execution.simplex_pivot_execution import (
    SimplexPivotExecution,
)

SEED = 729651269

LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    task = SimplexPivotExecution()
    out = []
    out.append("# Samples: P005v1 simplex_pivot_execution")
    out.append("")
    out.append("Two complete prompt/answer examples at levels 0, 2 and 5.")
    out.append("")
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        out.append("")
        task.config.set_level(level)
        for _ in range(LEVELS[level]):
            ex = task.generate_example()
            out.append("### Prompt")
            out.append("")
            out.append("```")
            out.append(task.render_prompt(ex.metadata))
            out.append("```")
            out.append("")
            out.append("**Answer**:")
            out.append("")
            out.append(f"`{ex.answer}`")
            out.append("")
    Path(__file__).with_name("samples_P005v1.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
