import random
from pathlib import Path

random.seed(3577985643)

from reasoning_core.tasks.generated.ua_global_over_greedy_r4.parametric_root_stability.parametric_root_stability import (
    ParametricRootStability,
)


def main():
    out = []
    for lvl in (0, 2, 5):
        task = ParametricRootStability()
        task.config.set_level(lvl)
        out.append(f"# Level {lvl}\n")
        for _ in range(2):
            e = task.generate_example()
            out.append("## Prompt\n")
            out.append(task.render_prompt(e.metadata))
            out.append("\n## Answer\n")
            out.append(e.answer)
            out.append("\n")
    target = Path(__file__).with_name("samples_P004v2.md")
    target.write_text("\n".join(out))


if __name__ == "__main__":
    main()
