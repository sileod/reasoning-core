import random
from pathlib import Path

from matroid_two_sum_independence import MatroidTwoSumIndependence


def main():
    random.seed(1139467751)
    task = MatroidTwoSumIndependence()
    out = Path(__file__).with_name("samples_P007v1.md")
    chunks = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        chunks.append(f"## Level {level}\n")
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            chunks.append(prompt + "\n")
            chunks.append("\nAnswer: " + ex.answer + "\n")
    out.write_text("\n".join(chunks), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
