import random
from pathlib import Path

import reasoning_core.tasks.generated.k3_language_implementation_r4.generator_reentry_trace.generator_reentry_trace as m

SEED = 4238614268
LEVELS = {0: 2, 2: 2, 5: 2}


def main():
    random.seed(SEED)
    task = m.ReentryTrace()
    out = Path(__file__).with_name("samples_P001v3.md")
    lines = []
    for level in (0, 2, 5):
        task.config.set_level(level)
        lines.append(f"## Level {level}")
        lines.append("")
        for _ in range(LEVELS[level]):
            ex = task.generate_example()
            assert task.score_answer(ex.answer, ex) == 1.0
            lines.append("### Prompt")
            lines.append("")
            lines.append(ex.prompt)
            lines.append("")
            lines.append("### Answer")
            lines.append("")
            lines.append(ex.answer)
            lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
