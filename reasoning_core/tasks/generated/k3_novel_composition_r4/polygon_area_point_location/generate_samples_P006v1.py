import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_novel_composition_r4.polygon_area_point_location.polygon_area_point_location import (
    PolygonAreaPointLocation,
)

random.seed(798610012)


def render_examples(task, level, count):
    task.config.set_level(level)
    examples = []
    for _ in range(count):
        e = task.generate_example()
        examples.append((task.render_prompt(e.metadata), e.answer))
    return examples


def main():
    task = PolygonAreaPointLocation()
    out = []
    for level in (0, 2, 5):
        out.append(f"## Level {level}\n")
        for prompt, answer in render_examples(task, level, 2):
            out.append("Prompt:\n")
            out.append(prompt)
            out.append("\nAnswer:\n")
            out.append(answer)
            out.append("\n")
    text = "\n".join(out)
    dest = Path(__file__).with_name("samples_P006v1.md")
    dest.write_text(text)


if __name__ == "__main__":
    main()
