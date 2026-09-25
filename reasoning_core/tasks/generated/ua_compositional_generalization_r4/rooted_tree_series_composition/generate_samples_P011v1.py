import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_compositional_generalization_r4.rooted_tree_series_composition.rooted_tree_series_composition import (
    RootedTreeSeriesComposition,
)

SEED = 2305351643


def main():
    random.seed(SEED)
    task = RootedTreeSeriesComposition()
    out_path = Path(__file__).with_name("samples_P011v1.md")
    chunks = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        chunks.append(f"## Level {level}")
        chunks.append("")
        for i in range(2):
            e = task.generate_example()
            chunks.append(f"### Example {i + 1}")
            chunks.append("")
            chunks.append(task.render_prompt(e.metadata))
            chunks.append("")
            chunks.append(f"Answer: {e.answer}")
            chunks.append("")
    out_path.write_text("\n".join(chunks), encoding="utf-8")
    print(out_path)


if __name__ == "__main__":
    main()
