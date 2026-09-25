import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_cognitive_psychology_r4.question_partition_equivalence.question_partition_equivalence import (
    QuestionPartitionEquivalence,
)


def main():
    random.seed(1336314872)
    task = QuestionPartitionEquivalence()
    out = Path(__file__).with_name("samples_P002v2.md")
    lines = ["# Samples: question_partition_equivalence", ""]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        for i in range(2):
            ex = task.generate_example(level=level)
            lines.append(f"### Example {i + 1}")
            lines.append("")
            lines.append("**Prompt:**")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("**Answer:**")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines))
    print(out)


if __name__ == "__main__":
    main()
