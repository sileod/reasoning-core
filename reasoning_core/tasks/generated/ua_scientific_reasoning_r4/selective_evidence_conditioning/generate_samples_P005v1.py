import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scientific_reasoning_r4.selective_evidence_conditioning.selective_evidence_conditioning import (
    SelectiveEvidenceConditioning,
)


def main():
    random.seed(729651269)
    task = SelectiveEvidenceConditioning()
    blocks = []
    blocks.append("# Samples for `selective_evidence_conditioning` (P005v1)")
    blocks.append("")
    for level in (0, 2, 5):
        blocks.append(f"## Level {level}")
        blocks.append("")
        for _ in range(2):
            entry = task.generate_example(level=level)
            prompt = entry.metadata.get("_prompt", task.render_prompt(entry.metadata))
            blocks.append("**Prompt:**")
            blocks.append("")
            for line in prompt.splitlines():
                blocks.append(f"> {line}")
            blocks.append("")
            blocks.append(f"**Answer:** `{entry.answer}`")
            blocks.append("")
    out = "\n".join(blocks)
    Path(__file__).with_name("samples_P005v1.md").write_text(out)


if __name__ == "__main__":
    main()
