import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_novel_composition_r1.loop_invariant_check import \
    loop_invariant_check as mod


def main():
    random.seed(2267388306)
    out = Path(__file__).with_name("samples_P003v1.md")
    task = mod.LoopInvariantCheck()
    lines = []
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        task.config.max_retries = 2000
        for _ in range(2):
            e = task.generate_example()
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(task.render_prompt(e.metadata))
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(e.answer)
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
