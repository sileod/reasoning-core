"""Generate the samples markdown for P001v1 (byte-reproducible under a fixed seed)."""

import random
from pathlib import Path

from reasoning_core.tasks.generated.ua_inference_modes_r4.knockout_agenda_control.knockout_agenda_control import (
    KnockoutAgendaControl,
)

SEED = 1662004003


def main():
    random.seed(SEED)
    task = KnockoutAgendaControl()
    out = Path(__file__).with_name("samples_P001v1.md")
    chunks = ["# P001v1 samples\n"]
    for level in (0, 2, 5):
        chunks.append("## Level %d\n" % level)
        for _ in range(2):
            ex = task.generate_example(level=level)
            chunks.append("Prompt:\n")
            chunks.append(ex.prompt + "\n")
            chunks.append("Answer:\n")
            chunks.append(ex.answer + "\n")
    out.write_text("\n".join(chunks) + "\n", encoding="utf-8")
    print("wrote", out)


if __name__ == "__main__":
    main()
