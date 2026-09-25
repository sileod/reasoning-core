import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_algorithms_and_data_structures_r4.material_frame_equivalence.material_frame_equivalence import (
    MaterialFrameEquivalence,
)


def _render_examples(level, n):
    t = MaterialFrameEquivalence()
    t.config.set_level(level)
    out = []
    for _ in range(n):
        ex = t.generate_example()
        out.append((ex.prompt, ex.answer))
    return out


def main():
    random.seed(1475571465)
    lines = ["# Samples for material_frame_equivalence (P002v1)"]
    for level in (0, 2, 5):
        lines.append("\n## Level %d\n" % level)
        for prompt, answer in _render_examples(level, 2):
            lines.append("**Prompt:**\n")
            lines.append(prompt)
            lines.append("\n**Answer:** %s\n" % answer)
    path = Path(__file__).with_name("samples_P002v1.md")
    path.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", path)


if __name__ == "__main__":
    main()
