import random
from pathlib import Path

from elimination_fill_in import EliminationFillIn

random.seed(798610012)

LEVELS = {0: 2, 2: 2, 5: 2}


def generate():
    task = EliminationFillIn()
    out = []
    for level, count in LEVELS.items():
        task.config.set_level(level)
        out.append(f"## Level {level}")
        for _ in range(count):
            x = task.generate_entry()
            out.append("")
            out.append(f"**Prompt:** {x.metadata}")
            out.append("")
            out.append(f"**Prompt rendered:** {task.render_prompt(x.metadata)}")
            out.append("")
            out.append(f"**Answer:** {x.answer}")
        out.append("")
    return "\n".join(out)


def main():
    text = generate()
    path = Path(__file__).with_name("samples_P006v1.md")
    path.write_text(text)


if __name__ == "__main__":
    main()
