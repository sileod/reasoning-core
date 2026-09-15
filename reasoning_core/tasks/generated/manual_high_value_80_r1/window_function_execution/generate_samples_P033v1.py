import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from reasoning_core.tasks.generated.manual_high_value_80_r1.window_function_execution.window_function_execution import (  # noqa: E402
    WindowFunctionExecution,
)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples_P033v1.md")


def main():
    random.seed(1403199800)
    task = WindowFunctionExecution()
    lines = ["# P033v1 samples\n"]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}\n")
        cfg = task.config_cls()
        cfg.set_level(level)
        task.config = cfg
        for _ in range(2):
            entry = task.generate_entry()
            lines.append("**Prompt:**\n")
            lines.append(entry.metadata["prompt"] + "\n")
            lines.append("**Answer:**\n")
            lines.append(entry.answer + "\n")
            lines.append("---\n")
    with open(OUT, "w") as f:
        f.write("\n".join(lines))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
