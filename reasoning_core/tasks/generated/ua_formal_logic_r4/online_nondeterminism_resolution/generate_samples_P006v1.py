import random
from pathlib import Path

random.seed(798610012)

from reasoning_core.tasks.generated.ua_formal_logic_r4.online_nondeterminism_resolution.online_nondeterminism_resolution import OnlineNondeterminismResolution

OUT = Path(__file__).with_name("samples_P006v1.md")


def main():
    task = OnlineNondeterminismResolution()
    lines = ["# Samples for online_nondeterminism_resolution (P006v1)", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"`{ex.answer}`")
            lines.append("")
    OUT.write_text("\n".join(lines))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
