import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_formal_logic_r4.call_by_need_thunk_accounting.call_by_need_thunk_accounting import (
    CallByNeedThunkAccounting,
)

SEED = 3577985643
OUT = Path(__file__).with_name("samples_P004v2.md")


def main():
    random.seed(SEED)
    task = CallByNeedThunkAccounting()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("# Level %d\n" % level)
        for _ in range(2):
            entry = task.generate_example()
            prompt = task.render_prompt(entry.metadata)
            lines.append("**Prompt:**\n\n```\n%s\n```\n" % prompt)
            lines.append("**Answer:** %s\n" % entry.answer)
        lines.append("\n")
    OUT.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
