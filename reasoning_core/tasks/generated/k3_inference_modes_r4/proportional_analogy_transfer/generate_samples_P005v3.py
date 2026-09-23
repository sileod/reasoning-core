"""Generate samples_P005v3.md with two complete examples at levels 0, 2, and 5."""

import random
from pathlib import Path

from reasoning_core.template import Task

from proportional_analogy_transfer import ProportionalAnalogyTransfer


def _render_answer(ex):
    from proportional_analogy_transfer import _render_domain_value
    if ex.metadata.mode == "name":
        return ex.answer
    return _render_domain_value(ex.metadata.domain, ex.answer)


def main():
    random.seed(1140349348)
    task = ProportionalAnalogyTransfer()
    out = []
    out.append("# samples_P005v3 - proportional_analogy_transfer")
    out.append("")
    for level in (0, 2, 5):
        out.append(f"## Level {level}")
        out.append("")
        for i in range(2):
            ex = task.generate_example(level=level)
            out.append(f"### Example {i + 1}")
            out.append("")
            out.append("**Prompt:**")
            out.append("")
            out.append(ex.prompt)
            out.append("")
            out.append("**Answer:**")
            out.append("")
            out.append(_render_answer(ex))
            out.append("")
    Path(__file__).with_name("samples_P005v3.md").write_text("\n".join(out))


if __name__ == "__main__":
    main()
