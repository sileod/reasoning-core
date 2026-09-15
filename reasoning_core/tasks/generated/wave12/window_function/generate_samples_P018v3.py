import random
from pathlib import Path

random.seed(2342189148)

from reasoning_core.tasks.generated.wave12.window_function_execution.window_function_execution import (
    WindowFunctionV3,
)

OUT = Path(__file__).with_name("samples_P018v3.md")


def format_entry(level, t):
    e = t.generate_example()
    return e, t.render_prompt(e.metadata), e.answer


def main():
    t = WindowFunctionV3()
    lines = []
    lines.append("# Samples: window_function_execution")
    lines.append("")
    lines.append("Random seed: 2342189148")
    lines.append("")
    for level in (0, 2, 5):
        t.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(2):
            e, prompt, answer = format_entry(level, t)
            lines.append("### Prompt")
            lines.append("")
            lines.append(prompt)
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(answer)
            lines.append("")
    OUT.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
