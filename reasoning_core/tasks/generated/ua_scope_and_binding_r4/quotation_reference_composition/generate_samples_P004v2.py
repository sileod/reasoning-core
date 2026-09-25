import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.quotation_reference_composition.quotation_reference_composition import (
    QuotationReferenceComposition,
)

SEED = 3577985643


def main():
    random.seed(SEED)
    task = QuotationReferenceComposition()
    out = []
    for level, tag in ((0, "Level 0"), (2, "Level 2"), (5, "Level 5")):
        task.config.set_level(level)
        out.append("## " + tag)
        out.append("")
        for i in range(2):
            x = task.generate_example()
            out.append("### Example %d" % (i + 1))
            out.append("")
            out.append("Prompt:")
            out.append("")
            out.append(task.render_prompt(x.metadata))
            out.append("")
            out.append("Answer: " + x.answer)
            out.append("")
    path = Path(__file__).with_name("samples_P004v2.md")
    path.write_text("\n".join(out) + "\n")
    print(path)
    print(out[0])


if __name__ == "__main__":
    main()
