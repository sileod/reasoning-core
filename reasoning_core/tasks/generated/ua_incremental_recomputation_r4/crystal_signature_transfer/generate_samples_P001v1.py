import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_incremental_recomputation_r4.\
    crystal_signature_transfer.crystal_signature_transfer import (
        CrystalSignatureTransfer,
        CrystalSignatureConfig,
    )


random.seed(1662004003)


def main():
    out = Path(__file__).with_name("samples_P001v1.md")
    lines = []
    lines.append("# Crystal Signature Transfer P001v1 - samples")
    lines.append("")
    t = CrystalSignatureTransfer(config=CrystalSignatureConfig())
    for level in (0, 2, 5):
        lines.append("## Level %d" % level)
        lines.append("")
        for k in range(2):
            ex = t.generate_example(level=level)
            lines.append("### Example %d" % (k + 1))
            lines.append("")
            lines.append("Prompt:")
            lines.append("")
            lines.append("```")
            lines.append(ex.prompt)
            lines.append("```")
            lines.append("")
            lines.append("Answer:")
            lines.append("")
            lines.append("```")
            lines.append(ex.answer)
            lines.append("```")
            lines.append("")
    out.write_text("\n".join(lines))
    print("wrote", out)


if __name__ == "__main__":
    main()
