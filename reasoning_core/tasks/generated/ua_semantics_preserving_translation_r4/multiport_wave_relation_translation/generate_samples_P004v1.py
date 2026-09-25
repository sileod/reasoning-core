import random
from pathlib import Path

random.seed(3536382515)

from reasoning_core.tasks.generated.ua_semantics_preserving_translation_r4.multiport_wave_relation_translation.multiport_wave_relation_translation import (
    MultiportWaveRelationTranslation,
)


def main():
    out = Path(__file__).with_name("samples_P004v1.md")
    chunks = []
    for level in (0, 2, 5):
        task = MultiportWaveRelationTranslation()
        task.config.set_level(level)
        chunks.append(f"## Level {level}\n")
        for n in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            chunks.append(f"### Example {n + 1}\n")
            chunks.append("Prompt:\n")
            chunks.append("```\n" + prompt + "\n```\n\n")
            chunks.append("Answer:\n")
            chunks.append("```\n" + ex.answer + "\n```\n\n")
    out.write_text("\n".join(chunks))


if __name__ == "__main__":
    main()
