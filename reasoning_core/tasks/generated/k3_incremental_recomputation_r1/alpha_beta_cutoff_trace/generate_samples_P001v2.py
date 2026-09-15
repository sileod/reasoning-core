import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_incremental_recomputation_r1.alphabeta_cutoff_trace.alphabeta_cutoff_trace import (
    AlphaBetaCutoffTraceV2,
)

SEED = 2302342651
OUT = Path(__file__).with_name("samples_P001v2.md")
LEVELS = {0: 3, 2: 3, 5: 3}


def main():
    random.seed(SEED)
    task = AlphaBetaCutoffTraceV2()
    lines = []
    for level, count in LEVELS.items():
        task.config.set_level(level)
        lines.append(f"## Level {level}\n")
        for i in range(count):
            x = task.generate_example()
            lines.append(f"### Example {i + 1}")
            lines.append("**Prompt**")
            lines.append(x.prompt)
            lines.append("")
            lines.append("**Answer**")
            lines.append(x.answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
