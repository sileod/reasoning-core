import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.filesystem_path_resolution.filesystem_path_resolution import (
    FilesystemPathResolution,
)


def generate_samples():
    random.seed(186835038)
    task = FilesystemPathResolution()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append("## Level %d\n" % level)
        for _ in range(2):
            entry = task.generate_example()
            out.append("**Prompt:** %s\n" % task.render_prompt(entry.metadata))
            out.append("**Answer:** %s\n" % entry.answer)
            out.append("")
    Path(__file__).with_name("samples_P020v2.md").write_text("\n".join(out))


if __name__ == "__main__":
    generate_samples()
