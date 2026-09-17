import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r2.stabilizer_tableau_simulation import (
    stabilizer_tableau_simulation as mod,
)


def main():
    random.seed(1211525277)
    task = mod.StabilizerTableauSimulation()
    lines = ["# Samples: stabilizer_tableau_simulation (P010v2)", ""]
    for level in [0, 2, 5]:
        task.config.set_level(level)
        lines.extend([f"## Level {level}", ""])
        for i in range(2):
            entry = task.generate_example()
            lines.extend([f"### Example {i + 1}", "", "Prompt:", "",
                          task.render_prompt(entry.metadata), "", f"Answer: {entry.answer}", ""])
    Path(__file__).with_name("samples_P010v2.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
