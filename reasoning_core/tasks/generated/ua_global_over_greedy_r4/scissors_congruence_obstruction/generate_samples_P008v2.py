"""Generate the samples_P008v2.md review file (byte-reproducible under a seed)."""

import pathlib
import random

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.scissors_congruence_obstruction.scissors_congruence_obstruction import (
    ScissorsCongruenceObstruction,
)

SEED = 3020341981

LEVELS = (0, 2, 5)
PER_LEVEL = 2


def main():
    random.seed(SEED)
    out_path = pathlib.Path(__file__).with_name("samples_P008v2.md")
    task = ScissorsCongruenceObstruction()
    chunks = []
    chunks.append("# samples_P008v2 - scissors_congruence_obstruction\n")
    for level in LEVELS:
        chunks.append(f"## Level {level}\n")
        for _ in range(PER_LEVEL):
            ex = task.generate_example(level=level)
            chunks.append("### Example\n")
            chunks.append("Prompt:\n")
            chunks.append("```\n" + ex.prompt + "\n```\n")
            chunks.append("Answer:\n")
            chunks.append("```\n" + ex.answer + "\n```\n")
    out_path.write_text("\n".join(chunks), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
