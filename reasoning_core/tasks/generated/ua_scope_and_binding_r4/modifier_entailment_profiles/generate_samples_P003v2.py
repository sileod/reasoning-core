import random
from pathlib import Path

random.seed(382564971)

from reasoning_core.tasks.generated.ua_scope_and_binding_r4.modifier_entailment_profiles.modifier_entailment_profiles import (
    ModifierEntailmentProfiles,
)


def main():
    out = Path(__file__).with_name("samples_P003v2.md")
    lines = [
        "# Samples for modifier_entailment_profiles (P003v2)",
        "",
        "Fixed predicate lexicon order: animate, concrete, material, liquid, container, edible, sharp.",
        "",
    ]
    for level in (0, 2, 5):
        lines.append(f"## Level {level}")
        lines.append("")
        t = ModifierEntailmentProfiles()
        t.config.set_level(level)
        for i in range(2):
            ex = t.generate_example()
            prompt = t.render_prompt(ex.metadata)
            lines.append(f"### Example {i+1}")
            lines.append("")
            lines.append(f"**Prompt:** {prompt}")
            lines.append("")
            lines.append(f"**Answer:** {ex.answer}")
            lines.append("")
    out.write_text("\n".join(lines))
    print(out.resolve())


if __name__ == "__main__":
    main()
