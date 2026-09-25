"""Generate the samples_P004v3.md review file (byte-reproducible under seed)."""

import pathlib
import random

from reasoning_core.tasks.generated.ua_planning_backtracking_r4.order_independent_tile_seeding.order_independent_tile_seeding import (
    OrderIndependentTileSeeding,
)


def main():
    random.seed(1339177894)
    out = pathlib.Path(__file__).with_name("samples_P004v3.md")
    lines = [
        "# order_independent_tile_seeding samples",
        "",
        "Task: choose a smallest forcing seed of board cells (under per-edge glue",
        "strengths and a temperature) so that every maximal legal attachment order",
        "places exactly all board cells.",
        "",
    ]
    for level in (0, 2, 5):
        for i in range(2):
            task = OrderIndependentTileSeeding()
            ex = task.generate_example(level=level)
            lines.append(f"## Level {level}")
            lines.append("")
            lines.append("### Prompt")
            lines.append("")
            lines.append("```")
            lines.append(ex.prompt)
            lines.append("```")
            lines.append("")
            lines.append(f"### Answer {i + 1}")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
