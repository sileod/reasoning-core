import random
from pathlib import Path

from reasoning_core.tasks.generated.wave12.information_seeking.information_seeking import (
    InformationSeeking,
)


def main():
    random.seed(2463459592)
    task = InformationSeeking()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"# Level {level}")
        for i in range(2):
            entry = task.generate_example()
            out.append(f"## Example {i + 1}")
            out.append("### Prompt")
            out.append(entry.metadata.get("_prompt",
                                          task.render_prompt(entry.metadata)))
            out.append("")
            out.append("### Answer")
            out.append(entry.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P003v1.md")
    path.write_text("\n".join(out))


if __name__ == "__main__":
    main()
