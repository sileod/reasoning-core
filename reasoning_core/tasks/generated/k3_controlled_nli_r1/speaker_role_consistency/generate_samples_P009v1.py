import random
from pathlib import Path

from reasoning_core.tasks.generated.k3_controlled_nli_r1.speaker_role_consistency.speaker_role_consistency import SpeakerRoleConsistency


def main():
    random.seed(3867019559)
    task = SpeakerRoleConsistency()
    lines = ["# Samples: P009v1", ""]
    for level in (0, 2, 5):
        task.config.set_level(level)
        for example in range(2):
            entry = task.generate_entry()
            lines.extend([f"## Level {level} example {example + 1}", "", "### Prompt", "",
                          task.render_prompt(entry.metadata), "", "### Answer", "", entry.answer, ""])
    Path(__file__).with_name("samples_P009v1.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
