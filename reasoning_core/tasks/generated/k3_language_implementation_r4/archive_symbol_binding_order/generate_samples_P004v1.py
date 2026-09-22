import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_language_implementation_r4.archive_symbol_binding_order.archive_symbol_binding_order import (
    ArchiveSymbolBindingOrder,
)

random.seed(3536382515)


def main():
    out = Path(__file__).with_name("samples_P004v1.md")
    task = ArchiveSymbolBindingOrder()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"# Level {level}")
        for idx in range(2):
            ex = task.generate_example()
            lines.append(f"## Example {idx + 1}")
            lines.append("**Answer**:")
            lines.append(ex.answer)
            lines.append("")
            lines.append("<details><summary>Prompt</summary>")
            lines.append("")
            lines.append("```")
            lines.append(ex.prompt)
            lines.append("```")
            lines.append("</details>")
            lines.append("")
    out.write_text("\n".join(lines) + "\n")
    print(out)


if __name__ == "__main__":
    main()
