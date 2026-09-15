import random

from pathlib import Path

from reasoning_core.tasks.generated.k3_shortcuts_fail_r1.envy_cycle_fair_allocation.envy_cycle_fair_allocation import (
    EnvyCycleFairAllocation,
)

SEED = 2072234021
LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    out = []
    task = EnvyCycleFairAllocation()
    for level, cnt in LEVELS.items():
        task.config.set_level(level)
        out.append("## Level {}".format(level))
        out.append("")
        for _ in range(cnt):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            out.append("### Example")
            out.append("")
            out.append("**Prompt:**")
            out.append("")
            out.append("```")
            out.append(prompt)
            out.append("```")
            out.append("")
            out.append("**Answer:**")
            out.append("")
            out.append(entry.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P005v2.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
