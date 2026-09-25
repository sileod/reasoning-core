import random
from pathlib import Path

from proof_net_link_repair import ProofNetLinkRepair

SEED = 1662004003
LEVELS = {0: 2, 2: 2, 5: 2}
OUT = Path(__file__).with_name("samples_P001v1.md")


def main():
    random.seed(SEED)
    task = ProofNetLinkRepair()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("## Level %d\n" % level)
        for i in range(LEVELS[level]):
            ex = task.generate_example()
            lines.append("### Example %d\n" % (i + 1))
            lines.append("**Prompt:**\n")
            lines.append(task.render_prompt(ex.metadata))
            lines.append("\n")
            lines.append("**Answer:**\n")
            lines.append(ex.answer)
            lines.append("\n")
    OUT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
