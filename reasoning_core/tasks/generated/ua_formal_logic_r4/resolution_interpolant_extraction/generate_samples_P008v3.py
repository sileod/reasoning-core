import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_formal_logic_r4.resolution_interpolant_extraction.resolution_interpolant_extraction import (
    ResolutionInterpolantExtraction,
)

random.seed(1618848011)

LEVELS = [0, 2, 5]


def render_example(task, metadata):
    return task.render_prompt(metadata)


def main():
    task = ResolutionInterpolantExtraction()
    out = []
    out.append("# samples_P008v3")
    out.append("")
    for level in LEVELS:
        task.config.set_level(level)
        out.append("## Level %d" % level)
        out.append("")
        for k in range(2):
            e = task.generate_example()
            prompt = task.render_prompt(e.metadata)
            out.append("### Example %d" % (k + 1))
            out.append("")
            out.append("Prompt:")
            out.append("```")
            out.append(prompt)
            out.append("```")
            out.append("")
            out.append("Answer:")
            out.append("```")
            out.append(e.answer)
            out.append("```")
            out.append("")
    target = Path(__file__).with_name("samples_P008v3.md")
    target.write_text("\n".join(out))


if __name__ == "__main__":
    main()
