import random
from pathlib import Path

from zigzag_cycle_survival import ZigzagCycleSurvival

random.seed(1475571465)


def main():
    task = ZigzagCycleSurvival()
    out = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        out.append("# Level {0}\n".format(level))
        for _ in range(2):
            ex = task.generate_example()
            out.append("**Prompt:**")
            out.append("```")
            out.append(ex.prompt)
            out.append("```")
            out.append("")
            out.append("**Answer:**")
            out.append("```")
            out.append(ex.answer)
            out.append("```")
            out.append("")
    path = Path(__file__).with_name("samples_P002v1.md")
    path.write_text("\n".join(out))
    print("wrote", path)


if __name__ == "__main__":
    main()
