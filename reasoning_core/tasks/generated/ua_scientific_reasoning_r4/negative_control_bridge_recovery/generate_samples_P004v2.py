"""Generate samples_P004v2.md for the negative-control bridge recovery task."""
import pathlib
import random

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.negative_control_bridge_recovery.negative_control_bridge_recovery import (
    NegativeControlBridgeRecovery,
)

random.seed(3577985643)

OUT = pathlib.Path(__file__).with_name("samples_P004v2.md")


def render(task, level):
    task.config.set_level(level)
    ex = task.generate_example()
    return task.render_prompt(ex.metadata), ex.answer


def main():
    task = NegativeControlBridgeRecovery()
    task.generate_example()  # warm build
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}")
        lines.append("")
        for j in range(2):
            prompt, answer = render(task, level)
            lines.append(f"## Example {j + 1}")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(answer)
            lines.append("")
    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
