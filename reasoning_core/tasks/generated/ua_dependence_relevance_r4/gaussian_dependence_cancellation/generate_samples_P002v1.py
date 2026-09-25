import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_dependence_relevance_r4.gaussian_dependence_cancellation.gaussian_dependence_cancellation import (
    GaussianDependenceCancellation,
)


def main():
    seed = 1475571465
    random.seed(seed)
    task = GaussianDependenceCancellation()
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append("# Level %d\n" % level)
        for _ in range(2):
            entry = task.generate_example()
            lines.append("Prompt:\n%s\n" % task.render_prompt(entry.metadata))
            lines.append("Answer:\n%s\n" % entry.answer)
    out = Path(__file__).with_name("samples_P002v1.md")
    out.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
