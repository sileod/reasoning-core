import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.leaky_evidence_commitment.leaky_evidence_commitment import (
    LeakyEvidenceCommitment,
)

SEED = 729651269
OUT = Path(__file__).with_name("samples_P005v1.md")


def _render(x):
    task = LeakyEvidenceCommitment()
    return task.render_prompt(x.metadata)


def main():
    random.seed(SEED)
    task = LeakyEvidenceCommitment()
    lines = [
        "# Samples for P005v1: leaky_evidence_commitment\n",
        "## Assigned design choice\n",
        LeakyEvidenceCommitment.design_choice + "\n",
        "## Summary\n",
        LeakyEvidenceCommitment.summary + "\n",
    ]
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"# Level {level}\n")
        for i in range(2):
            x = task.generate_example()
            lines.append("## Example " + str(i + 1) + "\n")
            lines.append(_render(x) + "\n")
            lines.append("\nAnswer: `" + x.answer + "`\n")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
