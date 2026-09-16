"""Generate samples_P008v2.md for the embedded_question_answerhood trial."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scope_and_binding_r1.embedded_question_answerhood.embedded_question_answerhood import (
    EmbeddedQuestionAnswerhood,
)

SEED = 3020341981
OUT = Path(__file__).with_name("samples_P008v2.md")


def main():
    random.seed(SEED)
    task = EmbeddedQuestionAnswerhood()
    lines = [
        "# Samples: embedded_question_answerhood (P008v2)",
        "",
        "Each example lists one or more sentences embedding a wh-question under know, tell "
        "or wonder. The gold answer is the ordered sequence of readings (exhaustive, "
        "mention-some, or pair-list), one per sentence.",
        "",
    ]
    for level in (0, 2, 5):
        task.config.set_level(level)
        examples = [task.generate_example() for _ in range(2)]
        lines.append(f"## Level {level}")
        lines.append("")
        for idx, ex in enumerate(examples, 1):
            lines.append(f"### Level {level} - Example {idx}")
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(ex.prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append(f"```\n{ex.answer}\n```")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
