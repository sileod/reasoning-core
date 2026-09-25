import random
from pathlib import Path

from reasoning_core.template import Task

from additive_preference_representability import AdditivePreferenceRepresentability


def main():
    random.seed(2305351643)
    task = AdditivePreferenceRepresentability()
    out = Path(__file__).with_name("samples_P011v1.md")
    chunks = []
    chunks.append("# Samples for P011v1\n")
    for lvl in (0, 2, 5):
        task.config.set_level(lvl)
        chunks.append(f"## Level {lvl}\n")
        for _ in range(2):
            ex = task.generate_example()
            prompt = task.render_prompt(ex.metadata)
            chunks.append(prompt)
            chunks.append("")
            chunks.append(f"**Answer**: {ex.answer}")
            chunks.append("")
        chunks.append("")
    out.write_text("\n".join(chunks))
    print(out)


if __name__ == "__main__":
    main()
