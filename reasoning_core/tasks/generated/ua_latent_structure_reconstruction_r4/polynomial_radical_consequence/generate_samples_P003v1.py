import random
from pathlib import Path

from polynomial_radical_consequence import PolynomialRadicalConsequence


def main():
    random.seed(2267388306)
    task = PolynomialRadicalConsequence()
    out = Path(__file__).with_name('samples_P003v1.md')
    lines = []
    for level in (0, 2, 5):
        lines.append(f"# Level {level}\n")
        task.config.set_level(level)
        for i in range(2):
            ex = task.generate_example()
            lines.append(f"## Example {i + 1}\n")
            lines.append("**Prompt:**\n")
            lines.append(ex.prompt + "\n")
            lines.append("**Answer:**\n")
            lines.append(ex.answer + "\n")
    out.write_text('\n'.join(lines), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
