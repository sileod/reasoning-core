import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

random.seed(1139467751)


def main():
    from hierarchical_knockout_compositing import HierarchicalKnockoutCompositing

    task = HierarchicalKnockoutCompositing()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append(f"# Level {level}\n")
        for _ in range(2):
            entry = task.generate_example()
            out.append(task.render_prompt(entry.metadata))
            out.append("")
            out.append("Answer: " + entry.answer)
            out.append("")
    Path(HERE / "samples_P007v1.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
