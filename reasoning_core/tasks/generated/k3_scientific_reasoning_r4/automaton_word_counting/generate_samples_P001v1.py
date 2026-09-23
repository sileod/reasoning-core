import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

random.seed(1662004003)

from automaton_word_counting import AutomatonWordCounting

out = Path(__file__).with_name("samples_P001v1.md")


def render_example(level):
    task = AutomatonWordCounting()
    task.config.set_level(level)
    x = task.generate_example()
    return task.render_prompt(x.metadata), x.answer


def section(level):
    lines = []
    for k in range(2):
        prompt, answer = render_example(level)
        lines.append("### Example %d" % (k + 1))
        lines.append("")
        lines.append("Prompt:")
        lines.append("")
        lines.append(prompt)
        lines.append("")
        lines.append("Answer:")
        lines.append("")
        lines.append(answer)
        lines.append("")
    return lines


def main():
    lines = []
    for level in (0, 2, 5):
        lines.append("## Level %d" % level)
        lines.append("")
        lines.extend(section(level))
    out.write_text("\n".join(lines) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
