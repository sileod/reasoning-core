import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_planning_backtracking_r4.terminal_network_coding.terminal_network_coding import (
    TerminalNetworkCoding,
)

__SEED__ = 368817805


def gen_samples(out_path, levels=(0, 2, 5), per_level=2):
    random.seed(__SEED__)
    lines = []
    for level in levels:
        lines.append(f"# Level {level}")
        lines.append("")
        task = TerminalNetworkCoding()
        task.config.set_level(level)
        for i in range(per_level):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append(f"## Example {i + 1} (level {level})")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append("```")
            lines.append(prompt)
            lines.append("```")
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(f"`{entry.answer}`")
            lines.append("")
            lines.append("---")
            lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    out = Path(__file__).with_name("samples_P002v3.md")
    gen_samples(out)
    print(f"wrote {out}")
