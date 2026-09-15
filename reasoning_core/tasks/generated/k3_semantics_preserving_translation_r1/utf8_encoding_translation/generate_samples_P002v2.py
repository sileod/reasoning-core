import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_semantics_preserving_translation_r1.utf8_encoding_translation.utf8_encoding_translation import (
    Utf8EncodingTranslation,
)

random.seed(1336314872)


def main():
    task = Utf8EncodingTranslation()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"## Level {level}")
        for _ in range(2):
            x = task.generate_example()
            out.append("### Example")
            out.append("**Prompt:**")
            out.append("")
            out.append(task.render_prompt(x.metadata))
            out.append("")
            out.append("**Answer:**")
            out.append("")
            out.append(x.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P002v2.md")
    path.write_text("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
