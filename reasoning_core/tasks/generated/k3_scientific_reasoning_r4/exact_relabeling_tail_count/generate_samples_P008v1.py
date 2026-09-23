import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_scientific_reasoning_r4.exact_relabeling_tail_count.exact_relabeling_tail_count import (
    ExactRelabelingTailCount,
)

random.seed(682015719)
TASK = ExactRelabelingTailCount()


def _write(path, level, n_examples):
    parts = [f"## Level {level}"]
    for _ in range(n_examples):
        TASK.config.set_level(level)
        ex = TASK.generate_example()
        parts.append("**Prompt:**")
        parts.append(TASK.render_prompt(ex.metadata))
        parts.append("")
        parts.append("**Answer:** " + ex.answer)
        parts.append("")
    return parts


def main():
    out = Path(__file__).with_name("samples_P008v1.md")
    lines = ["# Samples for exact_relabeling_tail_count (P008v1)", ""]
    lines += _write(out, 0, 2)
    lines += _write(out, 2, 2)
    lines += _write(out, 5, 2)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
